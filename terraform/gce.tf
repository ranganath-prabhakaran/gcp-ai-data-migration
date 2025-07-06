resource "google_compute_instance" "mcp_instance" {
  name         = "${var.resource_prefix}-mcp-instance"
  machine_type = "e2-medium"
  zone         = var.gcp_zone
  boot_disk { initialize_params { image = "debian-cloud/debian-11" } }
  network_interface {
    network    = google_compute_network.vpc_network.name
    subnetwork = google_compute_subnetwork.vpc_subnet.name
    access_config {}
  }
  service_account {
    email  = google_service_account.gce_service_account.email
    scopes = ["cloud-platform"]
  }
  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y git python3-pip default-mysql-client
    git clone "${var.git_repo_url}" /opt/migration-solution
    cd /opt/migration-solution
    pip3 install -r requirements.txt
    nohup bash -c 'python3 mcp_server/server.py' &
  EOT
  depends_on = [google_compute_instance.source_db_server]
}

resource "google_compute_instance" "source_db_server" {
  name         = "${var.resource_prefix}-source-db-server"
  machine_type = "e2-medium"
  zone         = var.gcp_zone
  boot_disk { initialize_params { image = "debian-cloud/debian-11" } }
  network_interface {
    network    = google_compute_network.vpc_network.name
    subnetwork = google_compute_subnetwork.vpc_subnet.name
  }
  service_account {
    email  = google_service_account.gce_service_account.email
    scopes = ["cloud-platform"]
  }
  metadata_startup_script = <<-EOT
    #!/bin/bash
    export DEBIAN_FRONTEND=noninteractive
    apt-get update
    apt-get install -y git mysql-server
    DB_ROOT_PASSWORD=$(gcloud secrets versions access latest --secret="${google_secret_manager_secret.db_password.secret_id}" --project="${var.gcp_project_id}")
    MIGRATION_USER_NAME=$(gcloud secrets versions access latest --secret="${google_secret_manager_secret.db_user.secret_id}" --project="${var.gcp_project_id}")
    mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$DB_ROOT_PASSWORD';"
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "CREATE USER '$MIGRATION_USER_NAME'@'%' IDENTIFIED BY '$DB_ROOT_PASSWORD';"
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON *.* TO '$MIGRATION_USER_NAME'@'%' WITH GRANT OPTION;"
    mysql -u root -p"$DB_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;"
    sed -i "s/127.0.0.1/0.0.0.0/g" /etc/mysql/mysql.conf.d/mysqld.cnf
    systemctl restart mysql
    git clone https://github.com/datacharmer/test_db.git /tmp/test_db
    mysql -u root -p"$DB_ROOT_PASSWORD" < /tmp/test_db/employees.sql
    gcloud secrets versions add ${google_secret_manager_secret.source_db_host.secret_id} --data-file=<(echo -n "${self.network_interface[0].network_ip}") --project="${var.gcp_project_id}"
  EOT
}
