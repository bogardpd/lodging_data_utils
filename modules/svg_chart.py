from lxml import etree as xml
from datetime import datetime
from modules.common import stay_mornings


class SVGChart:
    """ Creates an SVG chart from away and home period data. """

    _NSMAP = {None: "http://www.w3.org/2000/svg"}
    _PARAMS = {
        'night': {
            'cell_size': 8, # px
            'radius': 3, # px
        },
        'page': {
            'margin': 40, # px
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
        
        self.away_max = max(x['away']['nights'] for x in self.stays)
        self.home_max = max(x['home']['nights'] for x in self.stays)
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
        values['dims']['chart_height'] = (
            (len(self.stays) + 2) * PARAMS['night']['cell_size'])
        values['dims']['page_width'] = (double_margin
            + values['dims']['away_width'] + values['dims']['home_width'])
        values['dims']['page_height'] = (double_margin
            + values['dims']['chart_height'])
        
        values['coords']['axis_anchor'] = [
            PARAMS['page']['margin'] + values['dims']['away_width'],
            PARAMS['page']['margin']]
        values['coords']['chart_top_left'] = [
            PARAMS['page']['margin'],
            PARAMS['page']['margin']]
        values['coords']['chart_bottom_right'] = [
            (PARAMS['page']['margin']
                + values['dims']['away_width'] + values['dims']['home_width']),
            PARAMS['page']['margin'] + values['dims']['chart_height']]
        values['coords']['night_anchor'] = [
            values['coords']['axis_anchor'][0],
            (values['coords']['axis_anchor'][1]
                + (1.5 * PARAMS['night']['cell_size']))]

        return(values)

    def _draw_gridlines(self):
        """Draws vertical gridlines.
        
        Draws an axis, and draws gridlines every seven days.
        """

        PARAMS = self._PARAMS

        g_weeks = xml.SubElement(self._root, "g", id="weeks")

        week_x = list(range(int(-self.away_max/7), int(self.home_max/7) + 1))
        
        top = self._vals['coords']['chart_top_left'][1]
        bottom = self._vals['coords']['chart_bottom_right'][1]

        for week in week_x:
            style_class = 'axis' if week == 0 else 'gridline'
            x = (self._vals['coords']['night_anchor'][0]
                + (PARAMS['night']['cell_size'] * 7 * week))
            xml.SubElement(g_weeks, "line", x1 = str(x), y1 = str(top),
                x2 = str(x), y2 = str(bottom)).set('class', style_class)

    def _draw_nights(self):
        """Draws a dot for each night."""

        PARAMS = self._PARAMS
        
        g_nights = xml.SubElement(self._root, "g", id="nights")

        for i_row, row in enumerate(self.stays):
            
            away_purposes = []
            for loc in row['away']['cities']:
                away_purposes.extend(
                    loc['purpose'].lower() for i in range(loc['nights']))

            for i_night, purpose in enumerate(away_purposes):
                center = self._night_center(i_row, i_night,
                    row['away']['nights'])
                xml.SubElement(g_nights, "circle",
                    cx=str(center[0]),
                    cy=str(center[1]),
                    r=str(PARAMS['night']['radius'])).set(
                        'class', f"night-away-{purpose}")

            for i_night in range(row['home']['nights']):
                center = self._night_center(i_row, i_night)
                xml.SubElement(g_nights, "circle",
                    cx=str(center[0]),
                    cy=str(center[1]),
                    r=str(PARAMS['night']['radius'])).set(
                        'class', "night-home")
    
    def _draw_year_background(self, group, year,
                              start_coord, end_coord, fill_index):
        """Draws background shading for a specific year."""
        PARAMS = self._PARAMS
        left = self._vals['coords']['chart_top_left'][0]
        top = self._vals['coords']['chart_top_left'][1]
        right = self._vals['coords']['chart_bottom_right'][0]
        bottom = self._vals['coords']['chart_bottom_right'][1]
        half_cell = PARAMS['night']['cell_size'] / 2

        poly_coords = []
        # Create top points, left to right:
        if start_coord == None:
            # First year
            poly_coords.append([left, top])
            poly_coords.append([right, top])
        else:
            start_top = start_coord[1] - half_cell
            start_bottom = start_coord[1] + half_cell
            poly_coords.append([left, start_bottom])
            poly_coords.append([start_coord[0], start_bottom])
            poly_coords.append([start_coord[0], start_top])
            poly_coords.append([right, start_top])

        # Create bottom points, right to left:
        if end_coord == None:
            # Final year
            poly_coords.append([right, bottom])
            poly_coords.append([left, bottom])
        else:
            end_top = end_coord[1] - half_cell
            end_bottom = end_coord[1] + half_cell
            poly_coords.append([right, end_top])
            poly_coords.append([end_coord[0], end_top])
            poly_coords.append([end_coord[0], end_bottom])
            poly_coords.append([left, end_bottom])

        poly_points_str = " ".join(
            list(",".join(
                list(str(v) for v in p)
            ) for p in poly_coords)
        )
        xml.SubElement(group, "polygon", points=poly_points_str).set(
            'class', f"year-{fill_index}")
        if year:
            year_text = xml.SubElement(group, "text",
                x=str(poly_coords[0][0] + PARAMS['year']['text_offset'][0]),
                y=str(poly_coords[0][1] + PARAMS['year']['text_offset'][1]))
            year_text.set('class', "year-label")
            year_text.text = str(year)

    def _draw_year_backgrounds(self):
        """Draws background shading for all years."""

        COORDS = self._vals['coords']
        DIMS = self._vals['dims']
        PARAMS = self._PARAMS

        g_years = xml.SubElement(self._root, "g", id="year_background")
        
        # Determine [x, y] coordinates of each Jan 1 circle:
        year_starts = {}
        for row_index, row in enumerate(self.stays):
            for stay_loc in ['away', 'home']:
                if row[stay_loc]['start'].year < row[stay_loc]['end'].year:
                    # This stay contains a night ending on 1 January
                    mornings = stay_mornings(
                        row[stay_loc]['start'], row[stay_loc]['end'])
                    night_index = next(i for i, v in enumerate(mornings) if (
                        v.month == 1 and v.day == 1))
                    away_nights = (row[stay_loc]['nights'] if stay_loc == 'away'
                        else None)

                    year_starts[mornings[night_index].year] = (
                        self._night_center(
                            row_index, night_index, away_nights))
        
        years = sorted(year_starts.keys())
        if len(years) == 0:
            self._draw_year_background(g_years, None, None, None, 0)
        else:
            self._draw_year_background(
                g_years, years[0] - 1, None, year_starts.get(years[0]), 0)
            for i, year in enumerate(years):
                self._draw_year_background(
                    g_years,
                    year,
                    year_starts.get(year),
                    year_starts.get(year + 1),
                    (i + 1) % 2)

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
            style_tag.text = f"\n{f.read()}\n"

    def _night_center(self, row_index, night_index, away_nights=None):
        """Determines the coordinates of the center of a night dot."""
        cell_size = self._PARAMS['night']['cell_size']
        night_anchor = self._vals['coords']['night_anchor']
        if away_nights:
            x = (night_anchor[0]
                + ((night_index - away_nights) * cell_size))
        else:
            x = night_anchor[0] + ((night_index + 1) * cell_size)
        y = night_anchor[1] + (row_index * cell_size)
        return([x, y])

    def export(self, output_path):
        """Generates an SVG chart based on the away/home row values."""
        
        self._import_styles()
        self._draw_year_backgrounds()
        self._draw_gridlines()
        self._draw_nights()
                        
        tree = xml.ElementTree(self._root)
        tree.write(output_path, encoding='utf-8',
            xml_declaration=True, pretty_print=True)
        print(f"Wrote SVG to {output_path}")