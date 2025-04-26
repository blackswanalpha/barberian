# Barberian Project Archive

This archive contains the Barberian Barbershop Management System, ready for deployment to HostPinnacle or other hosting services.

## Archive Contents

This archive includes:
- All application code
- Templates and static files
- Configuration files for deployment
- Documentation

## Excluded Files

The following files and directories have been excluded from the archive:
- Virtual environment directories (`venv`, `env`)
- Git repository (`.git`)
- Python cache files (`__pycache__`, `*.pyc`, `*.pyo`, `*.pyd`)
- Database file (`db.sqlite3`)
- Media files (`media/*`)
- Compiled static files (`staticfiles`)
- Environment variables file (`.env`)
- External reference files (`brber-master`)

## Deployment Instructions

To deploy this archive to HostPinnacle:

1. Extract the archive:
   ```
   tar -xzvf barberian_YYYYMMDD.tar.gz
   ```

2. Create a `.env` file based on the `.env.example` template:
   ```
   cp .env.example .env
   ```

3. Edit the `.env` file with your production settings:
   - Set `DEBUG=False`
   - Add your domain to `ALLOWED_HOSTS`
   - Configure database settings
   - Configure email settings
   - Set a secure `SECRET_KEY`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Collect static files:
   ```
   python manage.py collectstatic --noinput
   ```

6. Run migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

8. Start the application with Gunicorn:
   ```
   gunicorn barberian.wsgi
   ```

For more detailed deployment instructions, refer to the `DEPLOYMENT.md` file included in the archive.

## Manifest

A manifest file (`barberian_manifest_YYYYMMDD.txt`) is included in the archive, listing all files that have been included.

## Support

For support or questions, please contact the development team or refer to the project documentation.
