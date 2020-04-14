from lxml import etree as xml


class SVGChart:
    """ Creates an SVG chart from trip and home stay data. """

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

    def export(self, output_path):
        """
        Generates an SVG chart based on the trip/home row values.
        """
        NSMAP = {None: "http://www.w3.org/2000/svg"}
        PARAMS = self.PARAMS

        away_max = max(x['away']['nights'] for x in self.stays)
        home_max = max(x['home']['nights'] for x in self.stays)
        
        away_width = away_max * PARAMS['night']['cell_size']
        home_width = home_max * PARAMS['night']['cell_size']
        
        page_width = (PARAMS['page']['margin'] * 2) + away_width + home_width
        page_height = ((PARAMS['page']['margin'] * 2)
            + (len(self.stays) * PARAMS['night']['cell_size']))
        
        root = xml.Element("svg", xmlns=NSMAP[None],
            width=str(page_width), height=str(page_height))

        # Create nights:
        nights = xml.SubElement(root, "g", id="nights")
        away_anchor = {
            'x': PARAMS['page']['margin'] + away_width,
            'y': PARAMS['page']['margin']}
        home_anchor = {
            'x': away_anchor['x'] + PARAMS['night']['cell_size'],
            'y': away_anchor['y']}
        for i, row in enumerate(self.stays):
            cell_size = PARAMS['night']['cell_size']           
            radius = PARAMS['night']['radius']
            
            away_purposes = []
            for loc in row['away']['cities']:
                away_purposes.extend(
                    loc['purpose'].lower() for i in range(loc['nights']))

            for j, purpose in enumerate(away_purposes):
                x = (away_anchor['x']
                    + ((j + 0.5 - row['away']['nights']) * cell_size))
                y = away_anchor['y'] + ((i + 0.5) * cell_size)
                fill = PARAMS['night']['away'][purpose]['fill']
                xml.SubElement(nights, "circle",
                    cx=str(x),
                    cy=str(y),
                    r=str(radius),
                    fill=fill)
            for j in range(row['home']['nights']):
                x = home_anchor['x'] + ((j + 0.5) * cell_size)
                y = home_anchor['y'] + ((i + 0.5) * cell_size)
                fill = PARAMS['night']['home']['fill']
                xml.SubElement(nights, "circle",
                    cx=str(x),
                    cy=str(y),
                    r=str(radius),
                    fill=fill)
                
        tree = xml.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True, pretty_print=True)
        print(f"Wrote SVG to {output_path}")