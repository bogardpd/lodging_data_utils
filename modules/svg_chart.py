from lxml import etree as xml
from datetime import datetime
from datetime import date
from datetime import timedelta
from modules.common import stay_mornings
from modules.common import first_morning


class SVGChart:
    """ Creates an SVG chart from away and home period data. """

    _NSMAP = {None: "http://www.w3.org/2000/svg"}
    _PARAMS = {
        'header': {
            'height': 40, # px
            'text_offset': [6, 25] # [x, y] px
        },
        'highlight': {
            'radius': 6, # px
        },
        'night': {
            'cell_size': 8, # px
            'radius': 3 # px
        },
        'page': {
            'margin': 40 # px
        },
        'year': {
            'margin': 50, # px
            'text_offset': [5, 15] # [x, y] px
        }
    }
    _STYLES_PATH = "styles/svg_chart.svg.css"

    def __init__(self, grouped_stay_rows, start_date=None, end_date=None):
        self.stays = self._filter_dates(grouped_stay_rows,
            start_date, end_date)
        
        self.away_max = max(a['away']['nights'] for a in self.stays)
        self.home_max = max(h['home']['nights'] for h in self.stays)
        self._vals = self._calculate_chart_values()

        self._root = xml.Element("svg", xmlns=self._NSMAP[None],
            width=str(self._vals['dims']['page_width']),
            height=str(self._vals['dims']['page_height']))

    def _calculate_chart_values(self):
        """Returns chart element dimensions and [x, y] coordinates."""
        PARAMS = self._PARAMS
        values = {'coords': {}, 'dims': {}}

        double_margin = 2 * PARAMS['page']['margin']

        values['dims']['away_width'] = ((1.5 + self.away_max)
            * PARAMS['night']['cell_size']
            + PARAMS['year']['margin'])
        values['dims']['home_width'] = ((1.5 + self.home_max)
            * PARAMS['night']['cell_size'])
        values['dims']['chart_width'] = (values['dims']['away_width']
            + values['dims']['home_width'])
        values['dims']['chart_height'] = (
            (len(self.stays) + 2) * PARAMS['night']['cell_size'])
        values['dims']['page_width'] = (double_margin
            + values['dims']['chart_width'])
        values['dims']['page_height'] = (double_margin
            + PARAMS['header']['height']
            + values['dims']['chart_height'])
        
        values['coords']['axis_anchor'] = [
            PARAMS['page']['margin'] + values['dims']['away_width'],
            PARAMS['page']['margin']]
        values['coords']['night_anchor'] = [
            values['coords']['axis_anchor'][0],
            (values['coords']['axis_anchor'][1]
                + PARAMS['header']['height']
                + (1.5 * PARAMS['night']['cell_size']))]
        values['coords']['header'] = {
            'l': PARAMS['page']['margin'],
            'r': PARAMS['page']['margin'] + values['dims']['chart_width'],
            't': PARAMS['page']['margin'],
            'b': PARAMS['page']['margin'] + PARAMS['header']['height']
        }
        values['coords']['chart'] = {
            'l': PARAMS['page']['margin'],
            'r': PARAMS['page']['margin'] + values['dims']['chart_width'],
            't': values['coords']['header']['b'],
            'b': (values['coords']['header']['b']
                + values['dims']['chart_height'])
        }

        return(values)

    def _create_groups(self):
        """Creates SVG groups.

        Ensures chart elements are layered appropriately.
        """
        self._g = {}
        
        ### Create groups, lowest layer to highest layer:
        groups = [
            'background',
            'gridlines',
            'header',
            'highlights',
            'nights']

        for group in groups:
            self._g[group] = xml.SubElement(self._root, "g", id=group)

    def _date_coords(self, find_morning):
        """Finds the coordinates of a specific night in the night grid.

        Looks for the date the night ends on.

        """
                       
        # Find row:
        row = next((i for i in self.stays if find_morning > i['away']['start'] and find_morning <= i['home']['end']), None)
        if row == None:
            return(None)
        row_index = self.stays.index(row)
        
        # Find night position relative to axis:
        if find_morning <= row['away']['end']:
            # Morning is in away period
            night_index = (find_morning - row['away']['end']).days - 1
        else:
            # Morning is in home period
            night_index = (find_morning - row['home']['start']).days

        return(self._night_center(row_index, night_index))

    def _draw_annotations(self):
        """Draws chart annotations."""
        
        # Highlight first (work) trip:
        first_away = self.stays[0]['away']
        self._draw_highlight(first_away, 'away')

        # Highlight longest away period:
        away_max = max(self.stays, key=lambda a:a['away']['nights'])['away']
        self._draw_highlight(away_max, 'away')

        # Highlight longest non-current home period:
        prior_home_max = max(self.stays[:-1],
            key=lambda h:h['home']['nights'])['home']
        self._draw_highlight(prior_home_max, 'home')

        # Highlight current (final) home period:
        current_home = self.stays[-1]['home']
        self._draw_highlight(current_home, 'home')

    def _draw_backgrounds(self):
        """Draws background shading."""

        COORDS = self._vals['coords']
        DIMS = self._vals['dims']
        PARAMS = self._PARAMS

        # Determine [x, y] coordinates of each Jan 1 circle:
        year_starts = {}
        for row_index, row in enumerate(self.stays):
            for stay_loc in ['away', 'home']:
                if row[stay_loc]['start'].year < row[stay_loc]['end'].year:
                    # This stay contains a night ending on 1 January
                    mornings = stay_mornings(
                        row[stay_loc]['start'], row[stay_loc]['end'])
                    night_indexes = [i for i, m in enumerate(mornings) if (
                        m.month == 1 and m.day == 1)]
                    
                    for morning in night_indexes:
                        if stay_loc == 'away':
                            night_index = morning - row['away']['nights']
                        else:
                            night_index = morning + 1
                        
                        year_starts[mornings[morning].year] = (
                            self._night_center(row_index, night_index))
        
        years = sorted(year_starts.keys())
        if len(years) == 0:
            self._draw_year_background(self._g['background'],
            None, None, None, 1)
        else:
            self._draw_year_background(self._g['background'],
                years[0] - 1, None, year_starts.get(years[0]), 1)
            for i, year in enumerate(years):
                self._draw_year_background(
                    self._g['background'],
                    year,
                    year_starts.get(year),
                    year_starts.get(year + 1),
                    i % 2)

    def _draw_gridlines(self):
        """Draws vertical gridlines.
        
        Draws an axis, and draws gridlines every seven days.
        """

        PARAMS = self._PARAMS

        week_x = list(range(int(-self.away_max/7), int(self.home_max/7) + 1))
        
        top = self._vals['coords']['chart']['t']
        bottom = self._vals['coords']['chart']['b']

        for week in week_x:
            style_class = 'axis' if week == 0 else 'gridline'
            x = (self._vals['coords']['night_anchor'][0]
                + (PARAMS['night']['cell_size'] * 7 * week))
            line_attr = {
                'x1': str(x),
                'y1': str(top),
                'x2': str(x),
                'y2': str(bottom),
                'class': style_class
            }
            xml.SubElement(self._g['gridlines'], "line", **line_attr)

    def _draw_header(self):
        """Draws a header."""

        axis_anchor = self._vals['coords']['axis_anchor']
        offset = self._PARAMS['header']['text_offset']
        bounds = self._vals['coords']['header']

        rect_attr = {
            'x': str(bounds['l']),
            'y': str(bounds['t']),
            'width': str(self._vals['dims']['chart_width']),
            'height': str(self._PARAMS['header']['height']),
            'class': "header"
        }
        xml.SubElement(self._g['header'], "rect", **rect_attr)

        line_attr = {
            'x1': str(bounds['l']),
            'y1': str(bounds['b']),
            'x2': str(bounds['r']),
            'y2': str(bounds['b']),
            'class': "axis"
        }
        xml.SubElement(self._g['header'], "line", **line_attr)

        header_away = xml.SubElement(self._g['header'], "text",
            x=str(axis_anchor[0] - offset[0]),
            y=str(axis_anchor[1] + offset[1]))
        header_away.set('class', "header header-away")
        header_away.text = "Nights on "
        header_away_business = xml.SubElement(header_away, "tspan")
        header_away_business.set('class', "header-sub night-away-business")
        header_away_business.text = "work"
        header_away_business.tail = "/"
        header_away_personal = xml.SubElement(header_away, "tspan")
        header_away_personal.set('class', "header-sub night-away-personal")
        header_away_personal.text = "personal"
        header_away_personal.tail = " trips"

        header_home = xml.SubElement(self._g['header'], "text",
            x=str(axis_anchor[0] + offset[0]),
            y=str(axis_anchor[1] + offset[1]))
        header_home.set('class', "header header-home")
        header_home.text = "Nights at "
        header_home_home = xml.SubElement(header_home, "tspan")
        header_home_home.set('class', "header-sub night-home")
        header_home_home.text = "home"

    def _draw_highlight(self, stay_period, style_class):
        """Draws a highlight behind a stay period."""
        end = stay_period['end']
        start = first_morning(end, stay_period['nights'])
        
        coords = []
        coords.append(self._date_coords(start))
        coords.append(self._date_coords(end))
        
        radius = self._PARAMS['highlight']['radius']
        rect_attr = {
            'x': str(coords[0][0] - radius),
            'y': str(coords[0][1] - radius),
            'rx': str(radius),
            'width': str(radius * 2 + coords[1][0] - coords[0][0]),
            'height': str(radius * 2),
            'class': f"highlight-{style_class}"
        }
        xml.SubElement(self._g['highlights'], "rect", **rect_attr)

    def _draw_nights(self):
        """Draws a dot for each night."""

        PARAMS = self._PARAMS
        
        for i_row, row in enumerate(self.stays):
            
            away_purposes = []
            for loc in row['away']['cities']:
                away_purposes.extend(
                    loc['purpose'].lower() for i in range(loc['nights']))

            for i_night, purpose in enumerate(away_purposes):
                center = self._night_center(
                    i_row, (i_night - row['away']['nights']))
                circle_attr = {
                    'cx': str(center[0]),
                    'cy': str(center[1]),
                    'r': str(PARAMS['night']['radius']),
                    'class': f"night-away-{purpose}"
                }
                xml.SubElement(self._g['nights'], "circle", **circle_attr)

            for i_night in range(row['home']['nights']):
                center = self._night_center(i_row, i_night + 1)
                circle_attr = {
                    'cx': str(center[0]),
                    'cy': str(center[1]),
                    'r': str(PARAMS['night']['radius']),
                    'class': "night-home"
                }
                xml.SubElement(self._g['nights'], "circle", **circle_attr)
    
    def _draw_year_background(self, group, year,
                              start_coord, end_coord, fill_index):
        """Draws background shading for a specific year."""
        PARAMS = self._PARAMS
        bounds = self._vals['coords']['chart']
        half_cell = PARAMS['night']['cell_size'] / 2
        
        poly_coords = []
        
        # Create top points, left to right:
        if start_coord == None:
            # First year
            poly_coords.append([bounds['l'], bounds['t']])
            poly_coords.append([bounds['r'], bounds['t']])
            
        else:
            start_top = start_coord[1] - half_cell
            start_bottom = start_coord[1] + half_cell
            poly_coords.append([bounds['l'], start_bottom])
            poly_coords.append([start_coord[0], start_bottom])
            poly_coords.append([start_coord[0], start_top])
            poly_coords.append([bounds['r'], start_top])

        # Create bottom points, right to left:
        if end_coord == None:
            # Final year
            poly_coords.append([bounds['r'], bounds['b']])
            poly_coords.append([bounds['l'], bounds['b']])
        else:
            end_top = end_coord[1] - half_cell
            end_bottom = end_coord[1] + half_cell
            poly_coords.append([bounds['r'], end_top])
            poly_coords.append([end_coord[0], end_top])
            poly_coords.append([end_coord[0], end_bottom])
            poly_coords.append([bounds['l'], end_bottom])

        poly_points_str = " ".join(
            list(",".join(
                list(str(v) for v in p)
            ) for p in poly_coords)
        )
        polygon_attr = {
            'points': poly_points_str,
            'class': f"year-{fill_index}"
        }
        xml.SubElement(group, "polygon", **polygon_attr)
        if year:
            year_attr = {
                'x': str(poly_coords[0][0] + PARAMS['year']['text_offset'][0]),
                'y': str(poly_coords[0][1] + PARAMS['year']['text_offset'][1]),
                'class': "year-label"
            }
            year_text = xml.SubElement(group, "text", **year_attr)
            year_text.text = str(year)

    def _filter_dates(self, grouped_stay_rows, start_date=None, end_date=None):
        """Filters group stay rows by date."""
        start_date = start_date or datetime.min.date() 
        end_date = end_date or datetime.max.date() 
        
        rows = list(filter(
            lambda r: r['away']['start'] >= start_date and r['away']['end'] <= end_date, grouped_stay_rows))
        
        return(rows)

    def _import_styles(self):
        """Imports styles from an external file."""        
        style_tag = xml.SubElement(self._root, "style")
        with open(self._STYLES_PATH) as f:
            lines = f.readlines()
            style_text = "\n"
            for line in lines:
                style_text += f"    {line}"
            style_text += "\n  "
            style_tag.text = style_text

    def _night_center(self, row_index, night_index):
        """Determines the coordinates of the center of a night dot."""
        cell_size = self._PARAMS['night']['cell_size']
        night_anchor = self._vals['coords']['night_anchor']
        
        x = night_anchor[0] + (night_index * cell_size)
        y = night_anchor[1] + (row_index * cell_size)

        return([x, y])

    def export(self, output_path):
        """Generates an SVG chart based on the away/home row values."""
        
        self._import_styles()
        self._create_groups()

        self._draw_header()
        self._draw_backgrounds()
        self._draw_gridlines()
        self._draw_nights()
        self._draw_annotations()

        tree = xml.ElementTree(self._root)
        tree.write(output_path, encoding='utf-8',
            xml_declaration=True, pretty_print=True)
        print(f"Wrote SVG to {output_path}")