# Operator Dashboard

This Software provides a dashboard for operational 3d printer data.

## Start

```bash
./app/operator_dashboard.py
```

Visit:
[http://hostname:6789/dashboard](http://hostname:6789/dashboard)

Here you can submit a filament change and annotate
 information to a print.


To view the status:
[http://hostname:6789/status](http://hostname:6789/status)


## Docker deployment

Build local Docker image:
```bash
sudo docker-compose up --build
```


## Add, edit or delete a filament

You can edit the filament list on
[http://hostname:6789/edit_filaments](http://hostname:6789/edit_filaments)

Be sure that you submit a valid json file.
If everything works well, you will be redirected to the valid json file.
