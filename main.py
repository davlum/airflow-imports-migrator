import os
import ast
import sys
from typing import List
import shutil
import argparse
import tempfile
import difflib

BASE_PACKAGES = [
    ('airflow.sensors.s3_key_sensor', 'airflow.providers.amazon.aws.sensors.s3_key'),
    ('airflow.sensors.time_delta_sensor', 'airflow.sensors.time_delta'),
    ('airflow.sensors.sql_sensor', 'airflow.sensors.sql'),
    ('airflow.sensors.hdfs_sensor', 'airflow.providers.apache.hdfs.sensors.hdfs'),
    ('airflow.sensors.date_time_sensor', 'airflow.sensors.date_time'),
    ('airflow.sensors.http_sensor', 'airflow.providers.http.sensors.http'),
    ('airflow.sensors.metastore_partition_sensor', 'airflow.providers.apache.hive.sensors.metastore_partition'),
    ('airflow.sensors.s3_prefix_sensor', 'airflow.providers.amazon.aws.sensors.s3_prefix'),
    ('airflow.sensors.named_hive_partition_sensor', 'airflow.providers.apache.hive.sensors.named_hive_partition'),
    ('airflow.sensors.base_sensor_operator', 'airflow.sensors.base'),
    ('airflow.sensors.web_hdfs_sensor', 'airflow.providers.apache.hdfs.sensors.web_hdfs'),
    ('airflow.sensors.hive_partition_sensor', 'airflow.providers.apache.hive.sensors.hive_partition'),
    ('airflow.sensors.external_task_sensor', 'airflow.sensors.external_task'),
    ('airflow.operators.postgres_operator', 'airflow.providers.postgres.operators.postgres'),
    ('airflow.operators.hive_stats_operator', 'airflow.providers.apache.hive.operators.hive_stats'),
    ('airflow.operators.druid_check_operator', 'airflow.providers.apache.druid.operators.druid_check'),
    ('airflow.operators.email_operator', 'airflow.operators.email'),
    ('airflow.operators.slack_operator', 'airflow.providers.slack.operators.slack'),
    ('airflow.operators.sqlite_operator', 'airflow.providers.sqlite.operators.sqlite'),
    ('airflow.operators.mssql_to_hive', 'airflow.providers.apache.hive.transfers.mssql_to_hive'),
    ('airflow.operators.hive_to_mysql', 'airflow.providers.apache.hive.transfers.hive_to_mysql'),
    ('airflow.operators.presto_check_operator', 'airflow.operators.sql'),
    ('airflow.operators.pig_operator', 'airflow.providers.apache.pig.operators.pig'),
    ('airflow.operators.mysql_to_hive', 'airflow.providers.apache.hive.transfers.mysql_to_hive'),
    ('airflow.operators.jdbc_operator', 'airflow.providers.jdbc.operators.jdbc'),
    ('airflow.operators.http_operator', 'airflow.providers.http.operators.http'),
    ('airflow.operators.s3_file_transform_operator', 'airflow.providers.amazon.aws.operators.s3_file_transform'),
    ('airflow.operators.oracle_operator', 'airflow.providers.oracle.operators.oracle'),
    ('airflow.operators.hive_to_druid', 'airflow.providers.apache.druid.transfers.hive_to_druid'),
    ('airflow.operators.subdag_operator', 'airflow.operators.subdag'),
    ('airflow.operators.hive_operator', 'airflow.providers.apache.hive.operators.hive'),
    ('airflow.operators.python_operator', 'airflow.operators.python'),
    ('airflow.operators.check_operator', 'airflow.operators.sql'),
    ('airflow.operators.hive_to_samba_operator', 'airflow.providers.apache.hive.transfers.hive_to_samba'),
    ('airflow.operators.docker_operator', 'airflow.providers.docker.operators.docker'),
    ('airflow.operators.branch_operator', 'airflow.operators.branch'),
    ('airflow.operators.s3_to_hive_operator', 'airflow.providers.apache.hive.transfers.s3_to_hive'),
    ('airflow.operators.mssql_operator', 'airflow.providers.microsoft.mssql.operators.mssql'),
    ('airflow.operators.latest_only_operator', 'airflow.operators.latest_only'),
    ('airflow.operators.mysql_operator', 'airflow.providers.mysql.operators.mysql'),
    ('airflow.operators.dagrun_operator', 'airflow.operators.trigger_dagrun'),
    ('airflow.operators.papermill_operator', 'airflow.providers.papermill.operators.papermill'),
    ('airflow.operators.google_api_to_s3_transfer', 'airflow.providers.amazon.aws.transfers.google_api_to_s3'),
    ('airflow.operators.gcs_to_s3', 'airflow.providers.amazon.aws.transfers.gcs_to_s3'),
    ('airflow.operators.bash_operator', 'airflow.operators.bash'),
    ('airflow.operators.redshift_to_s3_operator', 'airflow.providers.amazon.aws.transfers.redshift_to_s3'),
    ('airflow.operators.presto_to_mysql', 'airflow.providers.mysql.transfers.presto_to_mysql'),
    ('airflow.operators.sql_branch_operator', 'airflow.operators.sql'),
    ('airflow.operators.dummy_operator', 'airflow.operators.dummy'),
    ('airflow.operators.s3_to_redshift_operator', 'airflow.providers.amazon.aws.transfers.s3_to_redshift'),
    ('airflow.providers.amazon.aws.hooks.aws_dynamodb', 'airflow.providers.amazon.aws.hooks.dynamodb'),
    ('airflow.providers.cncf.kubernetes.backcompat.volume_mount', 'kubernetes.client.models.V1VolumeMount'),
    ('airflow.providers.cncf.kubernetes.backcompat.volume', 'kubernetes.client.models.V1Volume'),
    ('airflow.utils.log.wasb_task_handler', 'airflow.providers.microsoft.azure.log.wasb_task_handler'),
    ('airflow.utils.log.cloudwatch_task_handler', 'airflow.providers.amazon.aws.log.cloudwatch_task_handler'),
    ('airflow.utils.log.gcs_task_handler', 'airflow.providers.google.cloud.log.gcs_task_handler'),
    ('airflow.utils.log.es_task_handler', 'airflow.providers.elasticsearch.log.es_task_handler'),
    ('airflow.utils.log.stackdriver_task_handler', 'airflow.providers.google.cloud.log.stackdriver_task_handler'),
    ('airflow.utils.log.s3_task_handler', 'airflow.providers.amazon.aws.log.s3_task_handler'),
    ('airflow.contrib.sensors.qubole_sensor', 'airflow.providers.qubole.sensors.qubole'),
    ('airflow.contrib.sensors.bash_sensor', 'airflow.sensors.bash'),
    ('airflow.contrib.sensors.python_sensor', 'airflow.sensors.python'),
    ('airflow.contrib.sensors.wasb_sensor', 'airflow.providers.microsoft.azure.sensors.wasb'),
    ('airflow.contrib.sensors.sagemaker_tuning_sensor', 'airflow.providers.amazon.aws.sensors.sagemaker_tuning'),
    ('airflow.contrib.sensors.aws_athena_sensor', 'airflow.providers.amazon.aws.sensors.athena'),
    ('airflow.contrib.sensors.jira_sensor', 'airflow.providers.jira.sensors.jira'),
    ('airflow.contrib.sensors.aws_glue_catalog_partition_sensor', 'airflow.providers.amazon.aws.sensors.glue_catalog_partition'),
    ('airflow.contrib.sensors.sftp_sensor', 'airflow.providers.sftp.sensors.sftp'),
    ('airflow.contrib.sensors.emr_step_sensor', 'airflow.providers.amazon.aws.sensors.emr_step'),
    ('airflow.contrib.sensors.sagemaker_endpoint_sensor', 'airflow.providers.amazon.aws.sensors.sagemaker_endpoint'),
    ('airflow.contrib.sensors.hdfs_sensor', 'airflow.providers.apache.hdfs.sensors.hdfs'),
    ('airflow.contrib.sensors.gcs_sensor', 'airflow.providers.google.cloud.sensors.gcs'),
    ('airflow.contrib.sensors.pubsub_sensor', 'airflow.providers.google.cloud.sensors.pubsub'),
    ('airflow.contrib.sensors.weekday_sensor', 'airflow.sensors.weekday_sensor'),
    ('airflow.contrib.sensors.sagemaker_base_sensor', 'airflow.providers.amazon.aws.sensors.sagemaker_base'),
    ('airflow.contrib.sensors.redis_pub_sub_sensor', 'airflow.providers.redis.sensors.redis_pub_sub'),
    ('airflow.contrib.sensors.cassandra_record_sensor', 'airflow.providers.apache.cassandra.sensors.record'),
    ('airflow.contrib.sensors.sagemaker_transform_sensor', 'airflow.providers.amazon.aws.sensors.sagemaker_transform'),
    ('airflow.contrib.sensors.bigquery_sensor', 'airflow.providers.google.cloud.sensors.bigquery'),
    ('airflow.contrib.sensors.celery_queue_sensor', 'airflow.providers.celery.sensors.celery_queue'),
    ('airflow.contrib.sensors.emr_base_sensor', 'airflow.providers.amazon.aws.sensors.emr_base'),
    ('airflow.contrib.sensors.ftp_sensor', 'airflow.providers.ftp.sensors.ftp'),
    ('airflow.contrib.sensors.sagemaker_training_sensor', 'airflow.providers.amazon.aws.sensors.sagemaker_training'),
    ('airflow.contrib.sensors.azure_cosmos_sensor', 'airflow.providers.microsoft.azure.sensors.azure_cosmos'),
    ('airflow.contrib.sensors.aws_redshift_cluster_sensor', 'airflow.providers.amazon.aws.sensors.redshift'),
    ('airflow.contrib.sensors.emr_job_flow_sensor', 'airflow.providers.amazon.aws.sensors.emr_job_flow'),
    ('airflow.contrib.sensors.datadog_sensor', 'airflow.providers.datadog.sensors.datadog'),
    ('airflow.contrib.sensors.file_sensor', 'airflow.sensors.filesystem'),
    ('airflow.contrib.sensors.redis_key_sensor', 'airflow.providers.redis.sensors.redis_key'),
    ('airflow.contrib.sensors.cassandra_table_sensor', 'airflow.providers.apache.cassandra.sensors.table'),
    ('airflow.contrib.sensors.imap_attachment_sensor', 'airflow.providers.imap.sensors.imap_attachment'),
    ('airflow.contrib.sensors.mongo_sensor', 'airflow.providers.mongo.sensors.mongo'),
    ('airflow.contrib.sensors.aws_sqs_sensor', 'airflow.providers.amazon.aws.sensors.sqs'),
    ('airflow.contrib.task_runner.cgroup_task_runner', 'airflow.task.task_runner.cgroup_task_runner'),
    ('airflow.contrib.operators.gcp_tasks_operator', 'airflow.providers.google.cloud.operators.tasks'),
    ('airflow.contrib.operators.gcp_bigtable_operator', 'airflow.providers.google.cloud.operators.bigtable'),
    ('airflow.contrib.operators.sagemaker_model_operator', 'airflow.providers.amazon.aws.operators.sagemaker_model'),
    ('airflow.contrib.operators.datastore_export_operator', 'airflow.providers.google.cloud.operators.datastore'),
    ('airflow.contrib.operators.gcp_vision_operator', 'airflow.providers.google.cloud.operators.vision'),
    ('airflow.contrib.operators.adls_list_operator', 'airflow.providers.microsoft.azure.operators.adls_list'),
    ('airflow.contrib.operators.slack_webhook_operator', 'airflow.providers.slack.operators.slack_webhook'),
    ('airflow.contrib.operators.gcs_operator', 'airflow.providers.google.cloud.operators.gcs'),
    ('airflow.contrib.operators.gcs_delete_operator', 'airflow.providers.google.cloud.operators.gcs'),
    ('airflow.contrib.operators.vertica_to_hive', 'airflow.providers.apache.hive.transfers.vertica_to_hive'),
    ('airflow.contrib.operators.file_to_gcs', 'airflow.providers.google.cloud.transfers.local_to_gcs'),
    ('airflow.contrib.operators.gcp_compute_operator', 'airflow.providers.google.cloud.operators.compute'),
    ('airflow.contrib.operators.azure_container_instances_operator',
     'airflow.providers.microsoft.azure.operators.azure_container_instances'),
    ('airflow.contrib.operators.spark_jdbc_operator', 'airflow.providers.apache.spark.operators.spark_jdbc'),
    ('airflow.contrib.operators.gcp_natural_language_operator', 'airflow.providers.google.cloud.operators.natural_language'),
    ('airflow.contrib.operators.bigquery_get_data', 'airflow.providers.google.cloud.operators.bigquery'),
    ('airflow.contrib.operators.gcs_download_operator', 'airflow.providers.google.cloud.operators.gcs'),
    ('airflow.contrib.operators.gcp_translate_operator', 'airflow.providers.google.cloud.operators.translate'),
    ('airflow.contrib.operators.gcp_text_to_speech_operator', 'airflow.providers.google.cloud.operators.text_to_speech'),
    ('airflow.contrib.operators.dynamodb_to_s3', 'airflow.providers.amazon.aws.transfers.dynamodb_to_s3'),
    ('airflow.contrib.operators.aws_athena_operator', 'airflow.providers.amazon.aws.operators.athena'),
    ('airflow.contrib.operators.bigquery_operator', 'airflow.providers.google.cloud.operators.bigquery'),
    ('airflow.contrib.operators.sagemaker_tuning_operator', 'airflow.providers.amazon.aws.operators.sagemaker_tuning'),
    ('airflow.contrib.operators.opsgenie_alert_operator', 'airflow.providers.opsgenie.operators.opsgenie_alert'),
    ('airflow.contrib.operators.sagemaker_training_operator', 'airflow.providers.amazon.aws.operators.sagemaker_training'),
    ('airflow.contrib.operators.qubole_check_operator', 'airflow.providers.qubole.operators.qubole_check'),
    ('airflow.contrib.operators.gcp_sql_operator', 'airflow.providers.google.cloud.operators.cloud_sql'),
    ('airflow.contrib.operators.dingding_operator', 'airflow.providers.dingding.operators.dingding'),
    ('airflow.contrib.operators.dataflow_operator', 'airflow.providers.google.cloud.operators.dataflow'),
    ('airflow.contrib.operators.s3_delete_objects_operator', 'airflow.providers.amazon.aws.operators.s3_delete_objects'),
    ('airflow.contrib.operators.jira_operator', 'airflow.providers.jira.operators.jira'),
    ('airflow.contrib.operators.gcs_to_bq', 'airflow.providers.google.cloud.transfers.gcs_to_bigquery'),
    ('airflow.contrib.operators.emr_terminate_job_flow_operator', 'airflow.providers.amazon.aws.operators.emr_terminate_job_flow'),
    ('airflow.contrib.operators.kubernetes_pod_operator', 'airflow.providers.cncf.kubernetes.operators.kubernetes_pod'),
    ('airflow.contrib.operators.s3_copy_object_operator', 'airflow.providers.amazon.aws.operators.s3_copy_object'),
    ('airflow.contrib.operators.spark_submit_operator', 'airflow.providers.apache.spark.operators.spark_submit'),
    ('airflow.contrib.operators.gcs_list_operator', 'airflow.providers.google.cloud.operators.gcs'),
    ('airflow.contrib.operators.mlengine_operator', 'airflow.providers.google.cloud.operators.mlengine'),
    ('airflow.contrib.operators.sqoop_operator', 'airflow.providers.apache.sqoop.operators.sqoop'),
    ('airflow.contrib.operators.bigquery_to_mysql_operator', 'airflow.providers.google.cloud.transfers.bigquery_to_mysql'),
    ('airflow.contrib.operators.s3_to_sftp_operator', 'airflow.providers.amazon.aws.transfers.s3_to_sftp'),
    ('airflow.contrib.operators.jenkins_job_trigger_operator', 'airflow.providers.jenkins.operators.jenkins_job_trigger'),
    ('airflow.contrib.operators.redis_publish_operator', 'airflow.providers.redis.operators.redis_publish'),
    ('airflow.contrib.operators.databricks_operator', 'airflow.providers.databricks.operators.databricks'),
    ('airflow.contrib.operators.gcs_to_gdrive_operator', 'airflow.providers.google.suite.transfers.gcs_to_gdrive'),
    ('airflow.contrib.operators.grpc_operator', 'airflow.providers.grpc.operators.grpc'),
    ('airflow.contrib.operators.cassandra_to_gcs', 'airflow.providers.google.cloud.transfers.cassandra_to_gcs'),
    ('airflow.contrib.operators.snowflake_operator', 'airflow.providers.snowflake.operators.snowflake'),
    ('airflow.contrib.operators.bigquery_to_gcs', 'airflow.providers.google.cloud.transfers.bigquery_to_gcs'),
    ('airflow.contrib.operators.mongo_to_s3', 'airflow.providers.amazon.aws.transfers.mongo_to_s3'),
    ('airflow.contrib.operators.sftp_to_s3_operator', 'airflow.providers.amazon.aws.transfers.sftp_to_s3'),
    ('airflow.contrib.operators.s3_list_operator', 'airflow.providers.amazon.aws.operators.s3_list'),
    ('airflow.contrib.operators.gcp_dlp_operator', 'airflow.providers.google.cloud.operators.dlp'),
    ('airflow.contrib.operators.adls_to_gcs', 'airflow.providers.google.cloud.transfers.adls_to_gcs'),
    ('airflow.contrib.operators.sftp_operator', 'airflow.providers.sftp.operators.sftp'),
    ('airflow.contrib.operators.gcp_cloud_build_operator', 'airflow.providers.google.cloud.operators.cloud_build'),
    ('airflow.contrib.operators.gcp_translate_speech_operator', 'airflow.providers.google.cloud.operators.translate_speech'),
    ('airflow.contrib.operators.mysql_to_gcs', 'airflow.providers.google.cloud.transfers.mysql_to_gcs'),
    ('airflow.contrib.operators.discord_webhook_operator', 'airflow.providers.discord.operators.discord_webhook'),
    ('airflow.contrib.operators.aws_sqs_publish_operator', 'airflow.providers.amazon.aws.operators.sqs'),
    ('airflow.contrib.operators.gcs_to_gcs', 'airflow.providers.google.cloud.transfers.gcs_to_gcs'),
    ('airflow.contrib.operators.gcp_container_operator', 'airflow.providers.google.cloud.operators.kubernetes_engine'),
    ('airflow.contrib.operators.druid_operator', 'airflow.providers.apache.druid.operators.druid'),
    ('airflow.contrib.operators.winrm_operator', 'airflow.providers.microsoft.winrm.operators.winrm'),
    ('airflow.contrib.operators.sql_to_gcs', 'airflow.providers.google.cloud.transfers.sql_to_gcs'),
    ('airflow.contrib.operators.hive_to_dynamodb', 'airflow.providers.amazon.aws.transfers.hive_to_dynamodb'),
    ('airflow.contrib.operators.vertica_operator', 'airflow.providers.vertica.operators.vertica'),
    ('airflow.contrib.operators.spark_sql_operator', 'airflow.providers.apache.spark.operators.spark_sql'),
    ('airflow.contrib.operators.sns_publish_operator', 'airflow.providers.amazon.aws.operators.sns'),
    ('airflow.contrib.operators.gcp_speech_to_text_operator', 'airflow.providers.google.cloud.operators.speech_to_text'),
    ('airflow.contrib.operators.bigquery_to_bigquery', 'airflow.providers.google.cloud.transfers.bigquery_to_bigquery'),
    ('airflow.contrib.operators.gcp_spanner_operator', 'airflow.providers.google.cloud.operators.spanner'),
    ('airflow.contrib.operators.wasb_delete_blob_operator', 'airflow.providers.microsoft.azure.operators.wasb_delete_blob'),
    ('airflow.contrib.operators.s3_to_gcs_operator', 'airflow.providers.google.cloud.transfers.s3_to_gcs'),
    ('airflow.contrib.operators.azure_cosmos_operator', 'airflow.providers.microsoft.azure.operators.azure_cosmos'),
    ('airflow.contrib.operators.docker_swarm_operator', 'airflow.providers.docker.operators.docker_swarm'),
    ('airflow.contrib.operators.gcs_to_s3', 'airflow.providers.amazon.aws.transfers.gcs_to_s3'),
    ('airflow.contrib.operators.gcs_acl_operator', 'airflow.providers.google.cloud.operators.gcs'),
    ('airflow.contrib.operators.file_to_wasb', 'airflow.providers.microsoft.azure.transfers.file_to_wasb'),
    ('airflow.contrib.operators.sagemaker_base_operator', 'airflow.providers.amazon.aws.operators.sagemaker_base'),
    ('airflow.contrib.operators.ssh_operator', 'airflow.providers.ssh.operators.ssh'),
    ('airflow.contrib.operators.segment_track_event_operator', 'airflow.providers.segment.operators.segment_track_event'),
    ('airflow.contrib.operators.sagemaker_endpoint_operator', 'airflow.providers.amazon.aws.operators.sagemaker_endpoint'),
    ('airflow.contrib.operators.qubole_operator', 'airflow.providers.qubole.operators.qubole'),
    ('airflow.contrib.operators.imap_attachment_to_s3_operator', 'airflow.providers.amazon.aws.transfers.imap_attachment_to_s3'),
    ('airflow.contrib.operators.gcp_video_intelligence_operator', 'airflow.providers.google.cloud.operators.video_intelligence'),
    ('airflow.contrib.operators.postgres_to_gcs_operator', 'airflow.providers.google.cloud.transfers.postgres_to_gcs'),
    ('airflow.contrib.operators.datastore_import_operator', 'airflow.providers.google.cloud.operators.datastore'),
    ('airflow.contrib.operators.sagemaker_transform_operator', 'airflow.providers.amazon.aws.operators.sagemaker_transform'),
    ('airflow.contrib.operators.dataproc_operator', 'airflow.providers.google.cloud.operators.dataproc'),
    ('airflow.contrib.operators.mssql_to_gcs', 'airflow.providers.google.cloud.transfers.mssql_to_gcs'),
    ('airflow.contrib.operators.emr_create_job_flow_operator', 'airflow.providers.amazon.aws.operators.emr_create_job_flow'),
    ('airflow.contrib.operators.gcp_function_operator', 'airflow.providers.google.cloud.operators.functions'),
    ('airflow.contrib.operators.oracle_to_oracle_transfer', 'airflow.providers.oracle.transfers.oracle_to_oracle'),
    ('airflow.contrib.operators.bigquery_table_delete_operator', 'airflow.providers.google.cloud.operators.bigquery'),
    ('airflow.contrib.operators.bigquery_check_operator', 'airflow.providers.google.cloud.operators.bigquery'),
    ('airflow.contrib.operators.emr_add_steps_operator', 'airflow.providers.amazon.aws.operators.emr_add_steps'),
    ('airflow.contrib.operators.vertica_to_mysql', 'airflow.providers.mysql.transfers.vertica_to_mysql'),
    ('airflow.contrib.operators.ecs_operator', 'airflow.providers.amazon.aws.operators.ecs'),
    ('airflow.contrib.operators.awsbatch_operator', 'airflow.providers.amazon.aws.hooks.batch_client'),
    ('airflow.contrib.secrets.gcp_secrets_manager', 'airflow.providers.google.cloud.secrets.secret_manager'),
    ('airflow.contrib.secrets.hashicorp_vault', 'airflow.providers.hashicorp.secrets.vault'),
    ('airflow.contrib.secrets.aws_systems_manager', 'airflow.providers.amazon.aws.secrets.systems_manager'),
    ('airflow.contrib.secrets.aws_secrets_manager', 'airflow.providers.amazon.aws.secrets.secrets_manager'),
    ('airflow.contrib.secrets.azure_key_vault', 'airflow.providers.microsoft.azure.secrets.azure_key_vault'),
    ('airflow.contrib.utils.gcp_field_validator', 'airflow.providers.google.cloud.utils.field_validator'),
    ('airflow.contrib.utils.gcp_field_sanitizer', 'airflow.providers.google.cloud.utils.field_sanitizer'),
    ('airflow.contrib.utils.mlengine_operator_utils', 'airflow.providers.google.cloud.utils.mlengine_operator_utils'),
    ('airflow.contrib.utils', 'airflow.utils'),
    ('airflow.contrib.utils.weekday', 'airflow.utils.weekday'),
    ('airflow.contrib.utils.log.task_handler_with_custom_formatter', 'airflow.utils.log.task_handler_with_custom_formatter'),
    ('airflow.contrib.utils.log', 'airflow.utils.log'),
    ('airflow.contrib.hooks.vertica_hook', 'airflow.providers.vertica.hooks.vertica'),
    ('airflow.contrib.hooks.spark_jdbc_hook', 'airflow.providers.apache.spark.hooks.spark_jdbc'),
    ('airflow.contrib.hooks.bigquery_hook', 'airflow.providers.google.cloud.hooks.bigquery'),
    ('airflow.contrib.hooks.snowflake_hook', 'airflow.providers.snowflake.hooks.snowflake'),
    ('airflow.contrib.hooks.gcp_speech_to_text_hook', 'airflow.providers.google.cloud.hooks.speech_to_text'),
    ('airflow.contrib.hooks.jira_hook', 'airflow.providers.jira.hooks.jira'),
    ('airflow.contrib.hooks.aws_hook', 'airflow.providers.amazon.aws.hooks.base_aws'),
    ('airflow.contrib.hooks.gcp_spanner_hook', 'airflow.providers.google.cloud.hooks.spanner'),
    ('airflow.contrib.hooks.gcs_hook', 'airflow.providers.google.cloud.hooks.gcs'),
    ('airflow.contrib.hooks.aws_dynamodb_hook', 'airflow.providers.amazon.aws.hooks.dynamodb'),
    ('airflow.contrib.hooks.fs_hook', 'airflow.hooks.filesystem'),
    ('airflow.contrib.hooks.grpc_hook', 'airflow.providers.grpc.hooks.grpc'),
    ('airflow.contrib.hooks.qubole_hook', 'airflow.providers.qubole.hooks.qubole'),
    ('airflow.contrib.hooks.opsgenie_alert_hook', 'airflow.providers.opsgenie.hooks.opsgenie_alert'),
    ('airflow.contrib.hooks.databricks_hook', 'airflow.providers.databricks.hooks.databricks'),
    ('airflow.contrib.hooks.datastore_hook', 'airflow.providers.google.cloud.hooks.datastore'),
    ('airflow.contrib.hooks.ssh_hook', 'airflow.providers.ssh.hooks.ssh'),
    ('airflow.contrib.hooks.azure_cosmos_hook', 'airflow.providers.microsoft.azure.hooks.azure_cosmos'),
    ('airflow.contrib.hooks.winrm_hook', 'airflow.providers.microsoft.winrm.hooks.winrm'),
    ('airflow.contrib.hooks.gcp_container_hook', 'airflow.providers.google.cloud.hooks.kubernetes_engine'),
    ('airflow.contrib.hooks.sftp_hook', 'airflow.providers.sftp.hooks.sftp'),
    ('airflow.contrib.hooks.redshift_hook', 'airflow.providers.amazon.aws.hooks.redshift'),
    ('airflow.contrib.hooks.wasb_hook', 'airflow.providers.microsoft.azure.hooks.wasb'),
    ('airflow.contrib.hooks.aws_datasync_hook', 'airflow.providers.amazon.aws.hooks.datasync'),
    ('airflow.contrib.hooks.spark_sql_hook', 'airflow.providers.apache.spark.hooks.spark_sql'),
    ('airflow.contrib.hooks.gcp_natural_language_hook', 'airflow.providers.google.cloud.hooks.natural_language'),
    ('airflow.contrib.hooks.redis_hook', 'airflow.providers.redis.hooks.redis'),
    ('airflow.contrib.hooks.azure_container_volume_hook', 'airflow.providers.microsoft.azure.hooks.azure_container_volume'),
    ('airflow.contrib.hooks.gdrive_hook', 'airflow.providers.google.suite.hooks.drive'),
    ('airflow.contrib.hooks.jenkins_hook', 'airflow.providers.jenkins.hooks.jenkins'),
    ('airflow.contrib.hooks.gcp_pubsub_hook', 'airflow.providers.google.cloud.hooks.pubsub'),
    ('airflow.contrib.hooks.cloudant_hook', 'airflow.providers.cloudant.hooks.cloudant'),
    ('airflow.contrib.hooks.emr_hook', 'airflow.providers.amazon.aws.hooks.emr'),
    ('airflow.contrib.hooks.gcp_sql_hook', 'airflow.providers.google.cloud.hooks.cloud_sql'),
    ('airflow.contrib.hooks.gcp_cloud_build_hook', 'airflow.providers.google.cloud.hooks.cloud_build'),
    ('airflow.contrib.hooks.gcp_dlp_hook', 'airflow.providers.google.cloud.hooks.dlp'),
    ('airflow.contrib.hooks.discord_webhook_hook', 'airflow.providers.discord.hooks.discord_webhook'),
    ('airflow.contrib.hooks.dingding_hook', 'airflow.providers.dingding.hooks.dingding'),
    ('airflow.contrib.hooks.openfaas_hook', 'airflow.providers.openfaas.hooks.openfaas'),
    ('airflow.contrib.hooks.sqoop_hook', 'airflow.providers.apache.sqoop.hooks.sqoop'),
    ('airflow.contrib.hooks.gcp_dataflow_hook', 'airflow.providers.google.cloud.hooks.dataflow'),
    ('airflow.contrib.hooks.gcp_function_hook', 'airflow.providers.google.cloud.hooks.functions'),
    ('airflow.contrib.hooks.gcp_api_base_hook', 'airflow.providers.google.common.hooks.base_google'),
    ('airflow.contrib.hooks.gcp_transfer_hook', 'airflow.providers.google.cloud.hooks.cloud_storage_transfer_service'),
    ('airflow.contrib.hooks.mongo_hook', 'airflow.providers.mongo.hooks.mongo'),
    ('airflow.contrib.hooks.ftp_hook', 'airflow.providers.ftp.hooks.ftp'),
    ('airflow.contrib.hooks.salesforce_hook', 'airflow.providers.salesforce.hooks.salesforce'),
    ('airflow.contrib.hooks.gcp_compute_hook', 'airflow.providers.google.cloud.hooks.compute'),
    ('airflow.contrib.hooks.qubole_check_hook', 'airflow.providers.qubole.hooks.qubole_check'),
    ('airflow.contrib.hooks.aws_logs_hook', 'airflow.providers.amazon.aws.hooks.logs'),
    ('airflow.contrib.hooks.pinot_hook', 'airflow.providers.apache.pinot.hooks.pinot'),
    ('airflow.contrib.hooks.datadog_hook', 'airflow.providers.datadog.hooks.datadog'),
    ('airflow.contrib.hooks.cassandra_hook', 'airflow.providers.apache.cassandra.hooks.cassandra'),
    ('airflow.contrib.hooks.gcp_bigtable_hook', 'airflow.providers.google.cloud.hooks.bigtable'),
    ('airflow.contrib.hooks.gcp_dataproc_hook', 'airflow.providers.google.cloud.hooks.dataproc'),
    ('airflow.contrib.hooks.gcp_kms_hook', 'airflow.providers.google.cloud.hooks.kms'),
    ('airflow.contrib.hooks.aws_lambda_hook', 'airflow.providers.amazon.aws.hooks.lambda_function'),
    ('airflow.contrib.hooks.imap_hook', 'airflow.providers.imap.hooks.imap'),
    ('airflow.contrib.hooks.aws_sqs_hook', 'airflow.providers.amazon.aws.hooks.sqs'),
    ('airflow.contrib.hooks.azure_data_lake_hook', 'airflow.providers.microsoft.azure.hooks.azure_data_lake'),
    ('airflow.contrib.hooks.gcp_mlengine_hook', 'airflow.providers.google.cloud.hooks.mlengine'),
    ('airflow.contrib.hooks.sagemaker_hook', 'airflow.providers.amazon.aws.hooks.sagemaker'),
    ('airflow.contrib.hooks.gcp_text_to_speech_hook', 'airflow.providers.google.cloud.hooks.text_to_speech'),
    ('airflow.contrib.hooks.spark_submit_hook', 'airflow.providers.apache.spark.hooks.spark_submit'),
    ('airflow.contrib.hooks.segment_hook', 'airflow.providers.segment.hooks.segment'),
    ('airflow.contrib.hooks.azure_fileshare_hook', 'airflow.providers.microsoft.azure.hooks.azure_fileshare'),
    ('airflow.contrib.hooks.aws_glue_catalog_hook', 'airflow.providers.amazon.aws.hooks.glue_catalog'),
    ('airflow.contrib.hooks.slack_webhook_hook', 'airflow.providers.slack.hooks.slack_webhook'),
    ('airflow.contrib.hooks.pagerduty_hook', 'airflow.providers.pagerduty.hooks.pagerduty'),
    ('airflow.contrib.hooks.aws_athena_hook', 'airflow.providers.amazon.aws.hooks.athena'),
    ('airflow.contrib.hooks.gcp_tasks_hook', 'airflow.providers.google.cloud.hooks.tasks'),
    ('airflow.contrib.hooks.gcp_video_intelligence_hook', 'airflow.providers.google.cloud.hooks.video_intelligence'),
    ('airflow.contrib.hooks.gcp_translate_hook', 'airflow.providers.google.cloud.hooks.translate'),
    ('airflow.contrib.hooks.aws_firehose_hook', 'airflow.providers.amazon.aws.hooks.kinesis'),
    ('airflow.contrib.hooks.aws_sns_hook', 'airflow.providers.amazon.aws.hooks.sns'),
    ('airflow.contrib.hooks.gcp_vision_hook', 'airflow.providers.google.cloud.hooks.vision'),
    ('airflow.hooks.druid_hook', 'airflow.providers.apache.druid.hooks.druid'),
    ('airflow.hooks.base_hook', 'airflow.hooks.base'),
    ('airflow.hooks.http_hook', 'airflow.providers.http.hooks.http'),
    ('airflow.hooks.presto_hook', 'airflow.providers.presto.hooks.presto'),
    ('airflow.hooks.dbapi_hook', 'airflow.hooks.dbapi'),
    ('airflow.hooks.slack_hook', 'airflow.providers.slack.hooks.slack'),
    ('airflow.hooks.samba_hook', 'airflow.providers.samba.hooks.samba'),
    ('airflow.hooks.hive_hooks', 'airflow.providers.apache.hive.hooks.hive'),
    ('airflow.hooks.oracle_hook', 'airflow.providers.oracle.hooks.oracle'),
    ('airflow.hooks.jdbc_hook', 'airflow.providers.jdbc.hooks.jdbc'),
    ('airflow.hooks.mysql_hook', 'airflow.providers.mysql.hooks.mysql'),
    ('airflow.hooks.docker_hook', 'airflow.providers.docker.hooks.docker'),
    ('airflow.hooks.postgres_hook', 'airflow.providers.postgres.hooks.postgres'),
    ('airflow.hooks.webhdfs_hook', 'airflow.providers.apache.hdfs.hooks.webhdfs'),
    ('airflow.hooks.pig_hook', 'airflow.providers.apache.pig.hooks.pig'),
    ('airflow.hooks.zendesk_hook', 'airflow.providers.zendesk.hooks.zendesk'),
    ('airflow.hooks.S3_hook', 'airflow.providers.amazon.aws.hooks.s3'),
    ('airflow.hooks.hdfs_hook', 'airflow.providers.apache.hdfs.hooks.hdfs'),
    ('airflow.hooks.mssql_hook', 'airflow.providers.microsoft.mssql.hooks.mssql'),
    ('airflow.hooks.sqlite_hook', 'airflow.providers.sqlite.hooks.sqlite'),
    ('airflow.kubernetes.volume_mount', 'kubernetes.client.models.V1VolumeMount'),
    ('airflow.kubernetes.pod', 'kubernetes.client.models.V1VPod'),
    ('airflow.kubernetes.volume', 'kubernetes.client.models.V1Volume'),
    ('airflow.kubernetes.pod_runtime_info_env', 'kubernetes.client.models.V1EnvVar'),
]


def get_files(path: str) -> List[str]:
    return [f"{dirpath}/{file}" for dirpath, _, files in os.walk(path) for file in files]


def process_file(path: str, run: bool) -> str:
    with open(path) as f:
        file = f.read()
        old_file = file
        imports = get_imports(file)
        with tempfile.TemporaryDirectory() as tmpdirname:
            tmpfname = f"{tmpdirname}/{path}"
            os.makedirs(os.path.dirname(tmpfname))
            valid_pkgs = [(old, new) for old, new in BASE_PACKAGES if old in imports]
            for old_import, new_import in valid_pkgs:
                file = file.replace(old_import, new_import)

            d = difflib.Differ()
            diff = d.compare(old_file.splitlines(), file.splitlines())
            diff_str = f"{path}:\n" + "\n".join(diff)
            print(diff_str)
            if run:
                with open(tmpfname, "w+") as tmpf:
                    tmpf.write(file)
                    shutil.move(tmpfname, path)
            return diff_str


def get_imports(pyfile: str) -> List[str]:
    modules = []
    for node in ast.iter_child_nodes(ast.parse(pyfile)):
        if isinstance(node, ast.ImportFrom):
            if not node.names[0].asname:  # excluding the 'as' part of import
                modules.append(node.module)
        elif isinstance(node, ast.Import):  # excluding the 'as' part of import
            if not node.names[0].asname:
                modules.append(node.names[0].name)
    return modules


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Migrates Airflow imports. If --run is not set, the tool will make no changes and only print the diff.'
    )
    parser.add_argument('--path', type=dir_path, help='Path to migrate imports on.')
    parser.add_argument('--run', default=False, action='store_true', help='If not set, tool will only print diff.')

    args = parser.parse_args()
    if args.path is None:
        parser.print_help()
        sys.exit(0)

    file_paths = get_files(args.path)

    for file_path in file_paths:
        process_file(file_path, run=args.run)
