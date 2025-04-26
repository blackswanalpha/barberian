# Barberian Deployment to HostPinnacle

This package contains the Barberian Barbershop Management System, ready for deployment to HostPinnacle.

## Deployment Steps

### 1. Create a HostPinnacle Account

If you don't already have a HostPinnacle account, sign up at https://hostpinnacle.com/

### 2. Create a New Application

1. Log in to your HostPinnacle dashboard
2. Click "Create New App"
3. Choose a name for your application (e.g., "barberian")
4. Select the region closest to your target audience
5. Click "Create App"

### 3. Set Up PostgreSQL Database

1. Go to the "Resources" tab
2. Add a PostgreSQL database add-on
3. Choose a plan that fits your needs
4. Note the database credentials provided

### 4. Configure Environment Variables

1. Go to the "Settings" tab
2. Click "Reveal Config Vars"
3. Add the following environment variables:
   - `DEBUG`: Set to `False`
   - `SECRET_KEY`: Use a secure random key
   - `ALLOWED_HOSTS`: Add your app's domain
   - Database settings (from the database add-on):
     - `DB_ENGINE`: `django.db.backends.postgresql`
     - `DB_NAME`: Your database name
     - `DB_USER`: Your database user
     - `DB_PASSWORD`: Your database password
     - `DB_HOST`: Your database host
     - `DB_PORT`: Your database port (usually `5432`)
   - Email settings:
     - `EMAIL_BACKEND`: `django.core.mail.backends.smtp.EmailBackend`
     - `EMAIL_HOST`: Your SMTP server
     - `EMAIL_PORT`: Your SMTP port (usually `587`)
     - `EMAIL_USE_TLS`: `True`
     - `EMAIL_HOST_USER`: Your email address
     - `EMAIL_HOST_PASSWORD`: Your email password
   - Stripe settings (if applicable):
     - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
     - `STRIPE_SECRET_KEY`: Your Stripe secret key

### 5. Deploy the Application

1. Go to the "Deploy" tab
2. Connect your GitHub repository or upload this archive
3. Choose the branch you want to deploy (usually `main` or `master`)
4. Click "Deploy Branch"

### 6. Run Migrations

After deployment, run migrations to set up your database:

1. Go to the "More" dropdown menu
2. Select "Run Console"
3. Run the following command:
   ```
   python manage.py migrate
   ```

### 7. Create a Superuser

Create an admin user to access the Django admin panel:

1. Go to the "More" dropdown menu
2. Select "Run Console"
3. Run the following command:
   ```
   python manage.py createsuperuser
   ```
4. Follow the prompts to create a superuser

### 8. Verify Deployment

1. Click "Open App" to view your deployed application
2. Navigate to `/admin/` to access the Django admin panel
3. Log in with the superuser credentials you created

## Troubleshooting

If you encounter any issues during deployment, check the logs:

1. Go to the "More" dropdown menu
2. Select "View Logs"
3. Look for error messages that might help identify the problem

Common issues:
- Missing environment variables
- Database connection problems
- Static files not being served correctly

## Support

For support or questions, please contact the development team or refer to the project documentation.
