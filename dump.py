from deliverables import GlobalDeliverableData

# Change this to your actual shelf file name (without extension)
shelf_filename = 'Output/deliverables-04-30-23-23-58.shelve'  # No .db or .dat

output_filename = 'out.txt'

data = GlobalDeliverableData()
data._basename = "deliverable-output"
data.output()

