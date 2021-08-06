from main import get_files, process_file


def test_main():
    file_paths = get_files("fake_repo")

    for file_path in file_paths:
        print(file_path)
        res = process_file(file_path, run=False)
        assert res.strip() == f"""{file_path}:
- from airflow.operators.docker_operator import DockerOperator
?                             ---------

+ from airflow.providers.docker.operators.docker import DockerOperator
?             +++++++++++++++++
""".strip()
