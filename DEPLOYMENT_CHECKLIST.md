# Deployment Checklist for Barberian

Use this checklist to ensure you've completed all necessary steps before deploying to HostPinnacle.

## Pre-Deployment Checks

- [ ] Update `settings.py` for production:
  - [ ] Set `DEBUG = False` in production
  - [ ] Configure `ALLOWED_HOSTS`
  - [ ] Add `whitenoise` middleware
  - [ ] Configure `STATICFILES_STORAGE`

- [ ] Prepare necessary files:
  - [ ] `requirements.txt` with all dependencies
  - [ ] `Procfile` with gunicorn command
  - [ ] `runtime.txt` with Python version
  - [ ] `.env.example` with example environment variables

- [ ] Collect static files:
  - [ ] Run `python manage.py collectstatic --noinput`

- [ ] Test the application locally:
  - [ ] Run with production settings
  - [ ] Check all functionality
  - [ ] Verify static files are served correctly

## Deployment Steps

- [ ] Push code to GitHub repository
- [ ] Create application on HostPinnacle
- [ ] Configure environment variables on HostPinnacle
- [ ] Connect GitHub repository to HostPinnacle
- [ ] Deploy the application
- [ ] Run migrations on HostPinnacle
- [ ] Create a superuser on HostPinnacle
- [ ] Verify the application is working correctly

## Post-Deployment Checks

- [ ] Verify all pages load correctly
- [ ] Test user authentication
- [ ] Test appointment booking
- [ ] Test admin functionality
- [ ] Check email notifications
- [ ] Verify static files are served correctly
- [ ] Test responsive design on different devices

## Troubleshooting

If you encounter issues during deployment, check:

- [ ] Application logs on HostPinnacle
- [ ] Database connection
- [ ] Environment variables
- [ ] Static files configuration
- [ ] WSGI configuration

## Regular Maintenance

- [ ] Monitor application performance
- [ ] Regularly backup the database
- [ ] Keep dependencies updated
- [ ] Monitor error logs
- [ ] Apply security patches as needed
