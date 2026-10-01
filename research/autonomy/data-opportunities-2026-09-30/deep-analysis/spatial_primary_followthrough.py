import json
from spatial_marker_followthrough_actual import finite_primary_followthrough,clean
r=finite_primary_followthrough()
print("EMC_SPATIAL_PRIMARY_FOLLOWTHROUGH_BEGIN");print(json.dumps(clean(r)));print("EMC_SPATIAL_PRIMARY_FOLLOWTHROUGH_END")
