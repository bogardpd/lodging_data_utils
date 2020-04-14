from lxml import etree as xml


class SVGChart:
    """ Creates an SVG chart from trip and home stay data. """

    NSMAP = {None: "http://www.w3.org/2000/svg"}
    PARAMS = {
        'night': {
            'cell_size': 8, # px
            'radius': 3, # px
            'away':{
                'business': {
                    'fill': '#0077bb'
                },
                'personal': {
                    'fill': '#33bbee'
                }
            },    
            'home': {
                'fill': '#ee7733'
            }
        },
        'page': {
            'margin': 40, # px
        }     
    }
    TEMPLATE_PATH = 'templates/nights_away_and_home.svg'

    def __init__(self, stays_collection):
        self.stays = stays_collection
        self._vals = self._calculate_chart_values()

        self._root = xml.Element("svg", xmlns=self.NSMAP[None],
            width=str(self._vals['dims']['page_width']),
            height=str(self._vals['dims']['page_height']))

    def _calculate_chart_values(self):
        """Returns chart element dimensions and [x, y] coordinates."""
        PARAMS = self.PARAMS
        values = {'coords': {}, 'dims': {}}

        away_max = max(x['away']['nights'] for x in self.stays)
        home_max = max(x['home']['nights'] for x in self.stays)
        double_margin = 2 * PARAMS['page']['margin']

        values['dims']['away_width'] = ((1.5 + away_max)
            * PARAMS['night']['cell_size'])
        values['dims']['home_width'] = ((1.5 + home_max)
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
        values['coords']['night_anchor'] = [
            values['coords']['axis_anchor'][0],
            (values['coords']['axis_anchor'][1]
                + (1.5 * PARAMS['night']['cell_size']))]

        return(values)

    def _draw_axis(self):
        """Draws the chart away/home axis."""

        g_axis = xml.SubElement(self._root, "g", id="axis")

    def _draw_nights(self):
        """Draws a dot for each night."""

        COORDS = self._vals['coords']
        DIMS = self._vals['dims']
        PARAMS = self.PARAMS
        
        g_nights = xml.SubElement(self._root, "g", id="nights")

        for i_y, row in enumerate(self.stays):
            cell_size = PARAMS['night']['cell_size']           
            radius = PARAMS['night']['radius']
            
            away_purposes = []
            for loc in row['away']['cities']:
                away_purposes.extend(
                    loc['purpose'].lower() for i in range(loc['nights']))

            for i_x, purpose in enumerate(away_purposes):
                x = (COORDS['night_anchor'][0]
                    + ((i_x - row['away']['nights']) * cell_size))
                y = COORDS['night_anchor'][1] + (i_y * cell_size)
                fill = PARAMS['night']['away'][purpose]['fill']
                xml.SubElement(g_nights, "circle",
                    cx=str(x),
                    cy=str(y),
                    r=str(radius),
                    fill=fill)
                    
            for i_x in range(row['home']['nights']):
                x = COORDS['night_anchor'][0] + ((i_x + 1) * cell_size)
                y = COORDS['night_anchor'][1] + (i_y * cell_size)
                fill = PARAMS['night']['home']['fill']
                xml.SubElement(g_nights, "circle",
                    cx=str(x),
                    cy=str(y),
                    r=str(radius),
                    fill=fill)

    def export(self, output_path):
        """
        Generates an SVG chart based on the trip/home row values.
        """
        
        self._draw_nights()
        self._draw_axis()
        
        # self._root = xml.Element("svg", xmlns=NSMAP[None],
            # width=str(DIMS['page_width']), height=str(DIMS['page_height']))



        # away_max = max(x['away']['nights'] for x in self.stays)
        # home_max = max(x['home']['nights'] for x in self.stays)
        
        # away_width = away_max * PARAMS['night']['cell_size']
        # home_width = home_max * PARAMS['night']['cell_size']
        
        # page_width = ((PARAMS['page']['margin'] * 2)
        #     + (PARAMS['night']['cell_size'] * 3) + away_width + home_width)
        # page_height = ((PARAMS['page']['margin'] * 2)
        #     + (len(self.stays) * PARAMS['night']['cell_size']))
        

        
                
        tree = xml.ElementTree(self._root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        print(f"Wrote SVG to {output_path}")