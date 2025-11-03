from importlib.util import spec_from_file_location, module_from_spec
import tempfile, os
from datetime import datetime

path = r"d:\code\Airport_management_expert_system\application\airport_webapp\backend\chatbot_utils.py"
spec = spec_from_file_location("chatbot_utils", path)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

# Tests
print('parse_date ISO ->', mod.parse_date('2025-10-15'))
print('parse_date natural ->', mod.parse_date('when is it on 15th October'))
print('parse_flight_token 1 ->', mod.parse_flight_token('when will AI101 depart?'))
print('parse_flight_token 2 ->', mod.parse_flight_token('boeing 343 on 15th'))
print('parse_flight_token 3 ->', mod.parse_flight_token('flight 343'))

# create temp dump
tf = tempfile.NamedTemporaryFile(delete=False, suffix='.sql', mode='w', encoding='utf-8')
try:
    tf.write("INSERT INTO `flights` VALUES (1,'BOEING343',1,2,'2025-10-15T08:30:00','2025-10-15T12:00:00',3,'Scheduled');\n")
    tf.flush()
    path = tf.name
finally:
    tf.close()

dep = mod.find_in_sql_dump('BOEING343', datetime.fromisoformat('2025-10-15').date(), dump_path=path)
print('find_in_sql_dump ->', dep)

# cleanup
os.unlink(path)
print('OK')
