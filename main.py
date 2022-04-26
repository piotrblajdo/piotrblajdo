str = "user/bdu/data_quality/test_2/test_1.sql"
dest = "dags/wkf_data_quality/templates/end_user_tests/data_quality_bdu"
a_str = str.split("/")
print(f"{dest}/{a_str[-2]}/{a_str[-1]}")