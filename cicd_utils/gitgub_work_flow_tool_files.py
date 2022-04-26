"""Read changed_files.txt and uploads to GCS files listed there.

Deploying only folders "dags" and "plugins".
"""

import argparse
import os
import pandas as pd
from github import Github

FILE_EXCLUSIONS = ["/__pycache__/"]
COMPOSER_COMPONENT_DIR = ["dags"]
DAG_PATH = 'dags/'

repo_root = ""


# def create_or_checkout_branch(github, token, dest_dir, branch_name):
#     if check_branch(github, "piotrblajdo/destimation", branch_name):
#         commnad = f"""
#             git config --global user.email "piotrblajdo@gmail.com"
#             git config --global user.name "piotrblajdo"
#             git config -l | grep 'http\..*\.extraheader' | cut -d= -f1 | xargs -L1 git config --unset-all
#             git clone "https://piotrblajdo:{token}@github.com/piotrblajdo/destimation.git" "{dest_dir}"
#             ls -la "$CLONE_DIRECTORY"
#         """
#         clone_subprocess = subprocess.check_output(
#             commnad,
#             shell=True,
#         )


#
#         from github import Github
#
#         user = '****'
#         password = '****'
#
#         g = Github(user, password)
#         user = g.get_user()
#
#         repo_name = 'test'
#
#         # Check if repo non existant
#         if repo_name not in [r.name for r in user.get_repos()]:
#             # Create repository
#             user.create_repo(repo_name)
#
#         # Get repository
#         repo = user.get_repo(repo_name)
#
#         # File details
#         file_name = 'echo.py'
#         file_content = 'print("echo")'
#
#         # Create file
#         repo.create_file(file_name, 'commit', file_content)


def get_changed_files(changed_files_list_location):
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

    # changed_dag_set = set()
    # for file in changed_files_list:
    #     if DAG_PATH in file['filename']:
    #         foldername = DAG_PATH + file['filename'].split('/')[3]
    #         changed_dag_set.add(foldername)

    df_files = pd.DataFrame(columns=["filename", "status"])
    for f in changed_files_list:
        df_files = df_files.concat({"filename": f['filename'],
                                       "status": f['status']
                                        }, ignore_index=True)

    print(df_files)
    return df_files
#
# def sync_files(df, gcs_composer_bucket, dry_run=True):
#     """Synchronizes files from local (GIT) to the remote (GCS) by uploading changed files to GCS
#
#     Attributes:
#         df - dataframe with list of files from GCS and GIT, returned by get_changed_files function
#         gcs_composer_bucket - GCS composer bucket (with gs:// prefix)
#         dry_run - then True no files will be uploaded to the bucket.
#                   Only list will be printed (used in pull request).
#
#     Return:
#         N/A
#     """
#     if dry_run is False:
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(gcs_composer_bucket)
#     if dry_run is True:
#         print("\nThis is a dry run only. No files will be updated.")
#     else:
#         print("\nThis is a real execution. Files are updated in the bucket. ")
#
#     print("\nList of files to be copied to GCS:")
#     for index, row in df.sort_values("path").iterrows():
#         if any(comp_dir in row["full_path"] for comp_dir in COMPOSER_COMPONENT_DIR):
#             # print("GCS:", row["path"], " Local/Repo:", row["full_path"])
#             if dry_run is True:
#                 if row['status'] == 'removed':
#                     print("Deleting " + row["full_path"])
#                 else:
#                     print("Uploading " + row["full_path"] + " to " + row["path"])
#             else:
#                 blob = bucket.blob(row["path"])
#                 if row['status'] == 'removed':
#                     print("Deleting " + row["full_path"])
#                     try:
#                         blob.delete()
#                     except:
#                         print("File not found or error during deletion. ")
#                 else:
#                     print("Uploading " + row["full_path"] + " to " + row["path"])
#                     blob.upload_from_filename(row["full_path"])
#
#
# # def sync_folders(df, gcs_composer_bucket, dry_run=True):
# #     """Synchronizes fodlers from local (GIT) to the remote (GCS) by uploading changed files to GCS
#
# #     Attributes:
# #         df - dataframe with list of files from GCS and GIT, returned by get_changed_files function
# #         gcs_composer_bucket - GCS composer bucket (with gs:// prefix)
# #         dry_run - then True no files will be uploaded to the bucket.
# #                   Only list will be printed (used in pull request).
#
# #     Return:
# #         N/A
# #     """
#
# #     if dry_run is False:
# #         storage_client = storage.Client()
# #         bucket = storage_client.bucket(gcs_composer_bucket)
# #     if dry_run is True:
# #         print("\nThis is a dry run only. No files will be updated. [DAG directories]")
# #     else:
# #         print("\nThis is a real execution. Files are updated in the bucket. [DAG directories] ")
#
# #     print("List of folders to be copied to GCS (changed in pull request (dev) or since last release (prod)):")
# #     for index, row in df.sort_values("foldername").iterrows():
# #         print("Overwriting " + row["foldername"])
# #         gcs_dir = row["foldername"].split('src/composer/')[1]
#
# #         # Delete DAG folder content
# #         blobs = bucket.list_blobs(prefix=gcs_dir)
# #         for blob in blobs:
# #             print("Deleting", str(blob))
# #             if not dry_run:
# #                 blob.delete()
#
# #         # Upload all files in DAG folder
# #         for r, d, f in os.walk(row["foldername"]):
# #             for file in f:
# #                 gcs_file_path = os.path.join(r, file).split('src/composer/')[1]
# #                 print("Uploading " + os.path.join(r, file) + " to " + gcs_file_path)
# #                 if not dry_run:
# #                     blob = bucket.blob(gcs_file_path)
# #                     blob.upload_from_filename(os.path.join(r, file))
#
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deployment to GCS")
    # parser.add_argument("--dest_dir", action="store", dest="dest_dir", required=True)
    # parser.add_argument("--full_name_repo", action="store", dest="full_name_repo", required=True)
    # parser.add_argument("--branch", action="store", dest="branch", required=True)
    parser.add_argument("--changes_file", action="store", dest="changes_file", required=True,
                        help="Path to file with changes.")
    parser.add_argument("--source_dir", action="store", dest="source_dir", required=True)
    parser.add_argument("--dest_dir", action="store", dest="dest_dir", required=True)
    

    args = parser.parse_args()
    print(args.source_dir)
    print(args.dest_dir)
    df_files = get_changed_files(args.changes_file)
