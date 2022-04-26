"""Read changed_files.txt and uploads to GCS files listed there.

Deploying only folders "dags" and "plugins".
"""

import argparse
import os
import pandas as pd
import subprocess
from datetime import datetime
import shutil


def get_changed_files(changed_files_list_location, source_dir, dest_dir, branch_name):
    """Get list of files to upload.

    Reads content of /home/runner/work/changed_files.txt,
    which contains space separated list of all changed files in this pull request.
    Those are only files to be uploaded into GCS.

    Attributes:
        changed_files_list_location - location of file with list of files changed in pull request

    Return:
        Dataframe with list of files changed in pull request
    """

    with open(changed_files_list_location) as f:
        file_content = f.read()
        if file_content:
            raw_files_list = [path.strip() for path in file_content.split('\n')]
        else:
            raw_files_list = []
        changed_files_list = [{'filename': x[0], 'status': x[1]} for x in
                              zip(raw_files_list[::2], raw_files_list[1::2])]

    df_files = pd.DataFrame(columns=["filename", "status"])
    for f in changed_files_list:
        filename = f['filename']
        status = f['status']
        df = pd.DataFrame({"filename": [filename], "status": [status]})
        df_files = pd.concat([df_files, df], ignore_index=True, axis=0)

    for index, row in df_files.iterrows():
        dest_path = "dags/wkf_data_quality/templates/end_user_tests/data_quality_bdu"
        filename = row["filename"]
        if os.path.isdir(filename):
            continue
        l_filename = filename.split("/")
        dest_file = f"{dest_dir}/{dest_path}/{l_filename[-2]}/{l_filename[-1]}"

        if not os.path.exists(os.path.dirname(dest_file)):
            os.makedirs(os.path.dirname(dest_file))
        if os.path.exists(os.path.dirname(dest_file)):
            print(f"Destination dir exists")
        shutil.copy(f"{source_dir}/{filename}", dest_file)

        print(f"Source file name: {filename}")
        print(f"Destination file name: {dest_file}")
        print(f"Destination dir {dest_dir}/{dest_path}/{l_filename[-2]}")
        cp_cmd = f" cd {source_dir}  &&  cp -f {filename} {dest_file}"
        cp_cmd_result = subprocess.check_output(cp_cmd, shell=True)
        print(cp_cmd_result)
        cmd = f"stat {dest_file}"
        cp_cmd_result = subprocess.check_output(cmd, shell=True)
        print(cp_cmd_result)

        cmd_add = f" cd {dest_dir}  &&  git add {dest_file}"
        cmd_add_result = subprocess.check_output(cmd_add, shell=True)
        print(cmd_add_result)

    cmd_commit = f'cd {dest_dir} && git commit -m "{datetime.now()} - {branch_name}"'
    cmd_add_result = subprocess.check_output(cmd_commit, shell=True)

    cmd_push = f'cd {dest_dir} && git push origin {branch_name}'
    cmd_add_result = subprocess.check_output(cmd_push, shell=True)
    print(cmd_add_result)

    print(df_files)
    return df_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deployment to GCS")
    # parser.add_argument("--dest_dir", action="store", dest="dest_dir", required=True)
    # parser.add_argument("--full_name_repo", action="store", dest="full_name_repo", required=True)

    parser.add_argument("--changes_file", action="store", dest="changes_file", required=True,
                        help="Path to file with changes.")
    parser.add_argument("--source_dir", action="store", dest="source_dir", required=True)
    parser.add_argument("--dest_dir", action="store", dest="dest_dir", required=True)
    parser.add_argument("--branch_name", action="store", dest="branch_name", required=True)

    args = parser.parse_args()
    print(args.source_dir)
    print(args.dest_dir)
    print(args.branch_name)

    df_files = get_changed_files(args.changes_file, args.source_dir, args.dest_dir, args.branch_name)
