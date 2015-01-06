


se_colors = {
	'TV Application Layer':							'#D9D9D9',
	'Second Screen Framework':						'#B67272',
	'Audio Mining':									'#F23A3A',
	'Content Optimisation':							'#00B0F0',
	'HbbTV Application Toolkit':					'#FF91C4',
	
	'Open City Database':							'#61DDFF',
	'POIProxy':										'#C8F763',
	'App Generator':								'#1EC499',
	'Fusion Engine':								'#ECA2F5',
	'OpenDataSoft':									'#366092',
	'Recommendation as a Service':					'#FFC600',
	'Context Aware Recommendation':					'#037DA0',
	
	'Leaderboard':									'#FF8181',
	'Reality Mixer - Camera Artifact Rendering':	'#008A5F',
	'Reality Mixer - Reflection Mapping':			'#FFD92E',
	'Augmented Reality - Marker Tracking':			'#CCCCCC',
	'Augmented Reality - Fast Feature Tracking':	'#BEABD4',
	'Game Synchronization':							'#67B7D6',
	'Geospatial - POI Interface':					'#DBF5DA',
	'Geospatial - POI Matchmaking':					'#C4EAF5',
	'Visual Agent Design':							'#FFBB00',
	'Networked Virtual Character':					'#89B34B',
	
	'Content Enrichment':							'#F0C3A3',
	'Social Network':								'#FF33E7',
	'Content Sharing':								'#FFE0BF',
	'POI Storage':									'#91CCFF',
	'3D-Map Tiles':									'#FFAB52'
}

def select_bgcolor(se_name):
	if se_name not in se_colors:
		return "#FFFFFF"
		
	return se_colors[se_name]
