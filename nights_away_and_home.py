"""
This script generates a graphical representation of nights away and home
from hotel log data.
"""

# Standard imports
from datetime import date, datetime, timedelta
from pathlib import Path

# Third-party imports
import argparse
import pandas as pd
from dateutil import rrule
from lxml import etree as xml

# First-party imports
from modules.lodging_log import LodgingLog

# Define classes.

class GroupedStayCollection:
    """Groups consecutive away-from-home stays.

        Creates a list of dictionaries of away period/home period
        pairs, with details for each in nested dictionaries.
        """
    END_DATE = date.today()

    def __init__(self, start_evening=None, thru_morning=None):
        """Initialize a GroupedStayCollection."""
        self.log = LodgingLog()

        if start_evening is None:
            # Use the first morning in the log as the start date.
            self.start_morning = self.log.mornings().index.min().date()
            self.start_evening = self.start_morning - pd.Timedelta(days=1)
        else:
            self.start_morning = start_evening + pd.Timedelta(days=1)
            self.start_evening = start_evening

        if thru_morning is None:
            self.thru_morning = date.today()
        else:
            self.thru_morning = thru_morning

        self.groups = self._group_stays()

    def top(self, place):
        """Returns the top N stays of a given place (home/away)."""
        if place == "away":
            return sorted(
                [g for g in self.groups if g is not None and g.is_away],
                key=lambda g: g.nights,
                reverse=True,
            )
        elif place == "home":
            return sorted(
                [g for g in self.groups if g is not None and (not g.is_away)],
                key=lambda g: g.nights,
                reverse=True,
            )
        else:
            raise ValueError("Type must be 'away' or 'home'.")

    def _group_stays(self):
        """Groups consecutive away-from-home stays."""

        # Get lodging data from the log.
        lodging = self.log.mornings().copy()
        lodging['status'] = "Away"  # Default status for all stays.
        lodging = lodging[['status', 'purpose']]

        # Create a DataFrame with all mornings in the range.
        mornings = pd.DataFrame()
        mornings['morning'] = pd.date_range(
            start=self.start_morning,
            end=self.thru_morning,
            freq='D',
        )
        mornings = mornings.set_index('morning')

        # Merge the lodging data with the mornings DataFrame.
        mornings = pd.merge(
            mornings,
            lodging,
            left_index=True,
            right_index=True,
            how='left',
        )
        mornings['status'] = mornings['status'].fillna("Home")

        # Create a list of StayPeriod objects to group stays.
        grouped = []
        prev_m = None
        for m in mornings.itertuples():
            if len(grouped) == 0 or m.status != prev_m.status:
                # Create a new StayPeriod:
                if m.status == "Away":
                    grouped.append(
                        StayPeriod(True, m.Index.date(), m.purpose))
                else:
                    grouped.append(
                        StayPeriod(False, m.Index.date()))
            else:
                # Merge into previous group:
                if m.status == "Away":
                    grouped[-1].append_morning(m.purpose)
                else:
                    grouped[-1].append_morning()
            prev_m = m

        return grouped

    def rows(self):
        """Creates a row for each away period/home period pair.

        Calculates the length of each home stay between two away groups.
        """
        if self.groups[0].is_away:
            groups = self.groups
        else:
            # Rows must start with away. If the first group is home, add
            # a None value for the first row's Away.
            groups = [None] + self.groups
        rows = [
            {
                'away': groups[i],
                'home': groups[i + 1] if i + 1 < len(groups) else None
            }
            for i in range(0, len(groups), 2)
        ]
        return rows

class StayPeriod:
    """
    Contains details for a single home or away stay period.

    An away stay period may have multiple back to back hotel stays.
    """
    def __init__(self, is_away, end_date, purpose=None):
        """Initializes a StayPeriod with a single night."""
        self.is_away = is_away
        self.start_evening = end_date - pd.Timedelta(days=1)
        self.end_date = end_date
        self.nights = 1
        if is_away:
            self.purposes = [purpose]
        else:
            self.purposes = []

    def __str__(self):
        """Returns a StayPeriod as a string."""
        period_type = "Away" if self.is_away else "Home"
        return (f"{period_type} thru {self.end_date} "
                f"({self.nights} night{'s' if self.nights > 1 else ''})")

    def __repr__(self):
        """Returns a StayPeriod as a string."""
        period_type = "Away" if self.is_away else "Home"
        return (f"{period_type} thru {self.end_date} "
                f"({self.nights} night{'s' if self.nights > 1 else ''})")

    def append_morning(self, purpose=None):
        """
        Appends a morning to the stay period. This is used to extend the
        stay period by one night.
        """
        self.nights += 1
        self.end_date = self.end_date + pd.Timedelta(days=1)
        self.start_evening = self.end_date - pd.Timedelta(days=self.nights)
        if self.is_away:
            self.purposes.append(purpose)

    def date_range_string(self):
        """Returns a formatted string for the stay start and end dates.
        """
        start = self.start_evening
        end = self.end_date
        if start.year == end.year:
            if start.month == end.month:
                start_str = str(start.day)
            else:
                start_str = f"{start.day} {start:%b}"
        else:
            start_str = f"{start.day} {start:%b} {start.year}"
        end_str = f"{end.day} {end:%b} {end.year}"
        return f"{start_str}–{end_str}"

    def first_morning(self):
        """Returns the first morning of the stay period.

        This is the date after the checkin date.
        """
        return self.end_date - timedelta(days=self.nights-1)

class SVGChart:
    """ Creates an SVG chart from away and home period data. """

    _NSMAP = {None: "http://www.w3.org/2000/svg"}
    _PARAMS = {
        'chart': {
            'padding_bottom': 45 # px
        },
        'footer': {
            'padding_bottom': 16 # px
        },
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
        'note': {
            'text_offset': 22, # px
            'subtext_offset': 40 # px
        },
        'page': {
            'margin': 40 # px
        },
        'title': {
            'height': 85, # px
            'text_offset': 32, # px
            'subtext_offset': 66 # px
        },
        'year': {
            'margin': 50, # px
            'text_offset': [5, 15] # [x, y] px
        }
    }
    _STYLES_PATH = "styles/svg_chart.svg.css"

    def __init__(self, grouped_stay_collection):
        self.start_evening = grouped_stay_collection.start_evening
        self.thru_morning = grouped_stay_collection.thru_morning
        self.stays = grouped_stay_collection.rows()

        self.away_max = max(
            a['away'].nights for a in self.stays if a['away'] is not None
        )
        self.home_max = max(
            h['home'].nights for h in self.stays if h['home'] is not None
        )
        self._vals = self._calculate_chart_values()
        self.width = self._vals['dims']['page_width']
        self.height = self._vals['dims']['page_height']

        self._root = xml.Element(
            "svg", xmlns=self._NSMAP[None],
            width=str(self.width), height=str(self.height)
        )

        self._g = {} # Holds SVG groups for chart elements.

    def _calculate_chart_values(self):
        """Returns chart element dimensions and [x, y] coordinates."""
        params = self._PARAMS
        values = {'coords': {}, 'dims': {}}

        double_margin = 2 * params['page']['margin']

        values['dims']['away_width'] = ((1.5 + self.away_max)
            * params['night']['cell_size']
            + params['year']['margin'])
        values['dims']['home_width'] = ((1.5 + self.home_max)
            * params['night']['cell_size'])
        values['dims']['chart_width'] = (values['dims']['away_width']
            + values['dims']['home_width'])
        values['dims']['chart_height'] = (params['chart']['padding_bottom']
            + (len(self.stays) + 2) * params['night']['cell_size'])
        values['dims']['page_width'] = (double_margin
            + values['dims']['chart_width'])
        values['dims']['page_height'] = (double_margin
            + params['title']['height']
            + params['header']['height']
            + values['dims']['chart_height'])

        values['coords']['page_center'] = [
            values['dims']['page_width'] / 2,
            values['dims']['page_height'] / 2
        ]
        values['coords']['title'] = {
            't': params['page']['margin'],
            'b': params['page']['margin'] + params['title']['height'],
        }
        values['coords']['header'] = {
            'l': params['page']['margin'],
            'r': params['page']['margin'] + values['dims']['chart_width'],
            't': values['coords']['title']['b'],
            'b': values['coords']['title']['b'] + params['header']['height']
        }
        values['coords']['chart'] = {
            'l': params['page']['margin'],
            'r': params['page']['margin'] + values['dims']['chart_width'],
            't': values['coords']['header']['b'],
            'b': (values['coords']['header']['b']
                + values['dims']['chart_height'])
        }
        values['coords']['axis_anchor'] = [
            params['page']['margin'] + values['dims']['away_width'],
            values['coords']['header']['b']]
        values['coords']['night_anchor'] = [
            values['coords']['axis_anchor'][0],
            (values['coords']['axis_anchor'][1]
                + (1.5 * params['night']['cell_size']))]

        return values

    def _create_groups(self):
        """Creates SVG groups.

        Ensures chart elements are layered appropriately.
        """

        ### Create groups, lowest layer to highest layer:
        groups = [
            'page-background',
            'chart-background',
            'gridlines',
            'title',
            'header',
            'footer',
            'highlights',
            'nights',
            'notes']

        for group in groups:
            self._g[group] = xml.SubElement(self._root, "g", id=group)

    def _date_coords(self, find_morning):
        """
        Finds the coordinates of a specific night in the night grid.

        Looks for the date the night ends on.
        """
        # Find row:
        def in_row(row, check_date):
            """Returns the date range of a stay row."""
            if row['away'] is None:
                start = row['home'].start_evening
                end = row['home'].end_date
            elif row['home'] is None:
                start = row['away'].start_evening
                end = row['away'].end_date
            else:
                start = row['away'].start_evening
                end = row['home'].end_date
            return start < check_date <= end
        row = next(
            (
                i for i in self.stays
                if in_row(i, find_morning)
            ),
            None
        )
        if row is None:
            return None
        row_index = self.stays.index(row)

        # Find night position relative to axis:
        if row['away'] is not None and find_morning <= row['away'].end_date:
            # Morning is in away period
            night_index = (find_morning - row['away'].end_date).days - 1
        else:
            # Morning is in home period
            night_index = (find_morning - row['home'].start_evening).days

        return self._night_center(row_index, night_index)

    def _draw_annotations(self):
        """Draws chart annotations."""

        # Add each dot is one night label:
        first_home = self.stays[0]['home']
        self._draw_note(
            first_home.end_date,
            'end',
            "Each dot is one night 🠙",
            None,
            [2, -2],
        )

        # Highlight longest away period:
        away_max = max(
            self.stays,
            key=lambda a: (
                a['away'].nights if a['away'] is not None else 0
            )
        )['away']
        self._draw_highlight(away_max, 'away-personal')
        self._draw_note(away_max.first_morning(), 'start',
            f"{away_max.nights} nights away",
            away_max.date_range_string())

        # Highlight longest home period:
        home_max = max(
            self.stays,
            key=lambda h: (
                h['home'].nights if h['home'] is not None else 0
            )
        )['home']
        self._draw_highlight(home_max, 'home')
        self._draw_note(home_max.end_date, 'end',
            f"{home_max.nights} nights home",
            home_max.date_range_string())

    def _draw_chart_background(self):
        """Draws chart background shading."""

        # Determine [x, y] coordinates of each Jan 1 circle:
        year_starts = {}
        for row_index, row in enumerate(self.stays):
            for stay_loc in ['away', 'home']:
                if row[stay_loc] is None:
                    continue
                if row[stay_loc].start_evening.year < row[stay_loc].end_date.year:
                    # This stay contains a night ending on 1 January
                    mornings = self._stay_mornings(
                        row[stay_loc].start_evening, row[stay_loc].end_date)
                    night_indexes = [i for i, m in enumerate(mornings) if (
                        m.month == 1 and m.day == 1)]

                    for morning in night_indexes:
                        if stay_loc == 'away':
                            night_index = morning - row['away'].nights
                        else:
                            night_index = morning + 1

                        year_starts[mornings[morning].year] = (
                            self._night_center(row_index, night_index))

        years = sorted(year_starts.keys())
        group = self._g['chart-background']
        if len(years) == 0:
            self._draw_year_background(group, None, None, None, 1)
        else:
            self._draw_year_background(group, years[0] - 1, None,
                year_starts.get(years[0]), 1)
            for i, year in enumerate(years):
                self._draw_year_background(group, year,
                    year_starts.get(year), year_starts.get(year + 1), i % 2)

    def _draw_footer(self):
        """Draws the page footer."""

        y = self.height - self._PARAMS['footer']['padding_bottom']

        credit_attr = {
            'x': str(self._vals['coords']['chart']['l']),
            'y': str(y),
            'class': "footer credit"
        }
        credit = xml.SubElement(self._g['footer'], "text", **credit_attr)
        credit.text = " · ".join([
            "Created by Paul Bogard",
            "paulbogard.net",
            "github.com/bogardpd/hotel-data-utils"
        ])

        generated_attr = {
            'x': str(self._vals['coords']['chart']['r']),
            'y': str(y),
            'class': "footer date-generated"
        }
        generated = xml.SubElement(self._g['footer'], "text", **generated_attr)
        generated.text = f"Generated on {self._format_date(date.today())}"

    def _draw_gridlines(self):
        """Draws vertical gridlines.

        Draws an axis, and draws gridlines every seven days.
        """

        params = self._PARAMS

        week_x = list(range(int(-self.away_max/7), int(self.home_max/7) + 1))

        top = self._vals['coords']['chart']['t']
        bottom = self._vals['coords']['chart']['b']

        for week in week_x:
            style_class = 'axis' if week == 0 else 'gridline'
            x = (self._vals['coords']['night_anchor'][0]
                + (params['night']['cell_size'] * 7 * week))
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

        axis_x = self._vals['coords']['axis_anchor'][0]
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
            x=str(axis_x - offset[0]),
            y=str(bounds['t'] + offset[1]))
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
            x=str(axis_x + offset[0]),
            y=str(bounds['t'] + offset[1]))
        header_home.set('class', "header header-home")
        header_home.text = "Nights at "
        header_home_home = xml.SubElement(header_home, "tspan")
        header_home_home.set('class', "header-sub night-home")
        header_home_home.text = "home"

    def _draw_highlight(self, stay_period, style_class):
        """Draws a highlight behind a stay period."""
        if stay_period is None:
            return
        end = stay_period.end_date
        start = stay_period.first_morning()

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

        params = self._PARAMS

        for i_row, row in enumerate(self.stays):
            # Draw away nights
            if row['away'] is not None:
                for i_night, purpose in enumerate(row['away'].purposes):
                    center = self._night_center(
                        i_row, (i_night - row['away'].nights))
                    circle_attr = {
                        'cx': str(center[0]),
                        'cy': str(center[1]),
                        'r': str(params['night']['radius']),
                        'class': f"night-away-{purpose.lower()}"
                    }
                    xml.SubElement(self._g['nights'], "circle", **circle_attr)

            # Draw home nights
            if row['home'] is not None:
                for i_night in range(row['home'].nights):
                    center = self._night_center(i_row, i_night + 1)
                    circle_attr = {
                        'cx': str(center[0]),
                        'cy': str(center[1]),
                        'r': str(params['night']['radius']),
                        'class': "night-home"
                    }
                    xml.SubElement(self._g['nights'], "circle", **circle_attr)

    def _draw_note(self, night, align, note_text, subnote_text=None,
                   custom_offset=None):
        """Draws a text note."""
        if custom_offset is None:
            custom_offset = [0, 0]
        coords = self._date_coords(night)
        radius = self._PARAMS['night']['radius']

        if align == 'start':
            x = coords[0] - radius + custom_offset[0]
        else:
            x = coords[0] + radius + custom_offset[0]
        y = coords[1] + custom_offset[1]

        text_attr = {
            'x': str(x),
            'y': str(y + self._PARAMS['note']['text_offset']),
            'class': f"note note-{align}"
        }
        note = xml.SubElement(self._g['notes'], "text", **text_attr)
        note.text = note_text

        if subnote_text:
            subtext_attr = {
                'x': str(x),
                'y': str(y + self._PARAMS['note']['subtext_offset']),
                'class': f"note note-sub note-{align}"
            }
            subnote = xml.SubElement(self._g['notes'], "text", **subtext_attr)
            subnote.text = subnote_text.upper()

    def _draw_page_background(self):
        """Draws the page background color."""
        bg_attr = {
            'x': "0",
            'y': "0",
            'width': str(self.width),
            'height': str(self.height),
            'class': "page-background"
        }
        xml.SubElement(self._g['page-background'], "rect", **bg_attr)

    def _draw_title(self, title_text, subtitle_text):
        """Draws a title and subtitle."""

        x = self._vals['coords']['page_center'][0]
        title_params = self._PARAMS['title']
        title_coords = self._vals['coords']['title']
        title_attr = {
            'x': str(x),
            'y': str(title_coords['t'] + title_params['text_offset']),
            'class': "chart-title"
        }
        title = xml.SubElement(self._g['title'], "text", **title_attr)
        title.text = title_text

        subtitle_attr = {
            'x': str(x),
            'y': str(title_coords['t'] + title_params['subtext_offset']),
            'class': "chart-subtitle"
        }
        subtitle = xml.SubElement(self._g['title'], "text", **subtitle_attr)
        subtitle.text = subtitle_text.upper()


    def _draw_year_background(self, group, year,
                              start_coord, end_coord, fill_index):
        """Draws background shading for a specific year."""
        params = self._PARAMS
        bounds = self._vals['coords']['chart']
        half_cell = params['night']['cell_size'] / 2

        poly_coords = []

        # Create top points, left to right:
        if start_coord is None:
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
        if end_coord is None:
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
                'x': str(poly_coords[0][0] + params['year']['text_offset'][0]),
                'y': str(poly_coords[0][1] + params['year']['text_offset'][1]),
                'class': "year-label"
            }
            year_text = xml.SubElement(group, "text", **year_attr)
            year_text.text = str(year)

    def _filter_dates(self, grouped_stay_rows, start_evening=None, end_date=None):
        """Filters group stay rows by date."""
        start_evening = start_evening or datetime.min.date()
        end_date = end_date or datetime.max.date()

        rows = list(filter(
            lambda r: (r['away'].start >= start_evening
                and r['away'].end <= end_date),
            grouped_stay_rows))

        return rows

    def _import_styles(self):
        """Imports styles from an external file."""
        style_tag = xml.SubElement(self._root, "style")
        with open(self._STYLES_PATH, encoding='utf-8') as f:
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

    def _format_date(self, date_obj):
        """
        Formats a date object as a string. Necessary because strftime on
        Windows does not support non-zero-padded day numbers.
        """
        return "{d.day} {d:%b} {d.year}".format(d=date_obj)

    def _stay_mornings(self, start_evening, end_date):
        """
        Returns a list of morning dates in a given stay range. The start
        date is excluded from this list.
        """
        inclusive_date_range = [
            d.date() for d in list(
                rrule.rrule(rrule.DAILY, dtstart=start_evening, until=end_date)
            )
        ]
        return inclusive_date_range[1:]

    def export(self, output_path):
        """Generates an SVG chart based on the away/home row values."""

        self._import_styles()
        self._create_groups()

        self._draw_page_background()
        self._draw_title("Consecutive Nights Traveling or Home ",
            f"from {self._format_date(self.start_evening)} "
            f"to {self._format_date(self.thru_morning)}")
        self._draw_header()
        self._draw_chart_background()
        self._draw_gridlines()
        self._draw_nights()
        self._draw_annotations()
        self._draw_footer()

        tree = xml.ElementTree(self._root)
        tree.write(output_path, encoding='utf-8',
            xml_declaration=True, pretty_print=True)
        print(f"Wrote SVG to {output_path}")

# Main function to generate the nights away and home chart.

def nights_away_and_home(
    output_svg_file, output_stats_file, start_evening=None, thru_morning=None
):
    """Main function to generate nights away and home chart."""

    gsc = GroupedStayCollection(start_evening, thru_morning)

    svg = SVGChart(gsc)
    svg.export(output_svg_file)

    if output_stats_file is not None:
        with open(output_stats_file, 'w', encoding="utf-8") as f:
            f.write(
                f"Statistics for stays from {gsc.start_evening} to "
                f"{gsc.thru_morning}:\n\n")
            f.write("Top longest home stays:\n")
            for i, stay in enumerate(gsc.top("home")):
                f.write(f"  #{i + 1}\t{stay}\n")
            f.write("\nTop longest away stays:\n")
            for i, stay in enumerate(gsc.top("away")):
                f.write(f"  #{i + 1}\t{stay}\n")
        print(f"Wrote statistics to {output_stats_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a chart of nights away and home."
    )
    parser.add_argument('--output_svg',
        help="Path to save the output SVG file.",
        type=Path,
        required=True,
    )
    parser.add_argument('--output_stats',
        help="Path to save the statistics TXT file.",
        type=Path,
        default=None,
    )
    parser.add_argument('--start_evening',
        help="The first evening to include in the chart (YYYY-MM-DD).",
        type=date.fromisoformat,
    )
    parser.add_argument('--thru_morning',
        help="The last morning to include in the chart (YYYY-MM-DD).",
        type=date.fromisoformat,
    )
    args = parser.parse_args()

    nights_away_and_home(
        args.output_svg,
        args.output_stats,
        start_evening=args.start_evening,
        thru_morning=args.thru_morning,
    )
