import bent.annotate as bt

# Each element of the list corresponds to a different document text
#txt_list = [
#    'Caffeine is a central nervous system (CNS) stimulant. It is hypothesized that caffeine innhibits the activation NF-kappaB in A2058 melanoma cells.',
#    'The Parkinson disease is a degenerative disorder affecting the motor system. PARK2 gene expression is associated with the Parkinson disease.']

txt_list = "Reed's Sindrome has several manifestations and symptoms."

bt.annotate(
        recognize=True,
        link=True,
        types={
            'disease': 'medic',
            'cell_line': 'cellosaurus',
            'bioprocess': ''
               },
        input_text=txt_list,
        out_dir='output/'
)