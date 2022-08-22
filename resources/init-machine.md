# How to initialize a machine for this presentation

## Box Creation and DNS

1. Create a box on Hetzner using Ubuntu 22.04.
2. [Configure the DNS for
   matrixbotworkshop.com](https://domains.google.com/registrar/matrixbotworkshop.com/dns)
   to have an `A` record pointing to the IP of the box.

## Setup the box

From an SSH session on the box:

1. Install Dependencies

   ```sh
   apt update && apt upgrade -y
   apt install -y \
      docker.io \
      nginx \
      certbot python3-certbot-nginx \
      python3-virtualenv
   ```

2. Generate the Synapse config

   ```
   docker run -it --rm \
      --mount type=volume,src=synapse-data,dst=/data \
      -e SYNAPSE_SERVER_NAME=matrixbotworkshop.com \
      -e SYNAPSE_REPORT_STATS=no \
      matrixdotorg/synapse:latest generate
   ```

3. Edit the homeserver config in
   `/var/lib/docker/volumes/synapse-data/_data/homeserver.yaml`

   1. Disable federation in the config by removing `federation` from
      `listeners.resources[0].names`
   2. Add `enable_registration: true`
   3. Add `enable_registration_without_verification: true`

4. Run synapse

   ```
   docker run -d --name synapse \
       --mount type=volume,src=synapse-data,dst=/data \
       -p 8008:8008 \
       matrixdotorg/synapse:latest
   ```

5. Setup nginx reverse proxy. Edit
   `/etc/nginx/sites-available/matrixbotworkshop.com` and put the following
   content:

   ```
   server {
       listen 80;
       listen [::]:80;
   
       server_name matrixbotworkshop.com;

       location /_matrix/maubot/v1/logs {
           proxy_pass http://localhost:29316;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "Upgrade";
           proxy_set_header X-Forwarded-For $remote_addr;
       }

       location /_matrix/maubot {
           proxy_pass http://localhost:29316;
           proxy_set_header X-Forwarded-For $remote_addr;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header Host $host;

           # Nginx by default only allows file uploads up to 1M in size
           # Increase client_max_body_size to match max_upload_size defined in homeserver.yaml
           client_max_body_size 50M;
       }
   
       location ~ ^(/_matrix/client|/_synapse/client) {
           proxy_pass http://localhost:8008;
           proxy_set_header X-Forwarded-For $remote_addr;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_set_header Host $host;
   
           # Nginx by default only allows file uploads up to 1M in size
           # Increase client_max_body_size to match max_upload_size defined in homeserver.yaml
           client_max_body_size 50M;
       }
   }
   ```

   (See https://matrix-org.github.io/synapse/latest/reverse_proxy.html#nginx)

6. Restart `ngnix`: `systemctl restart nginx`

7. Get a certificate for the

   ```
   sudo certbot --nginx -d matrixbotworkshop.com -d www.matrixbotworkshop.com
   ```

8. Follow https://docs.mau.fi/maubot/usage/setup/index.html#production-setup
   until step 5.

   1. Use `/var/lib/maubot` as the directory to store the config in.
   2. Change the `server.public_url` to `https://matrixbotworkshop.com`
   3. Change the `homeservers` to have `matrixbotworkshop.com` (use the
      registration secret from Synapse)
   4. Add a `demo: matrixiscool` entry to `admins`

9. Create a systemd service for maubot.

   1. Create `/etc/systemd/system/maubot.service` with the following content:

      ```
      [Unit]
      Description=Maubot
      
      [Service]
      ExecStart=/var/lib/maubot/bin/python -m maubot
      WorkingDirectory=/var/lib/maubot
      
      [Install]
      WantedBy=multi-user.target
      ```

   2. Start it with `systemctl start maubot`
