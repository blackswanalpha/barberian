# Deploying Barberian to HostPinnacle

This guide will walk you through the steps to deploy the Barberian application to HostPinnacle.

## Prerequisites

1. A HostPinnacle account
2. Git installed on your local machine
3. Your project code pushed to a Git repository (GitHub, GitLab, etc.)

## Step 1: Prepare Your Project

Make sure your project has the following files:

- `requirements.txt`: Lists all Python dependencies
- `Procfile`: Tells HostPinnacle how to run your application
- `runtime.txt`: Specifies the Python version
- `.env.example`: Example environment variables (rename to `.env` on the server)

## Step 2: Log in to HostPinnacle

1. Log in to your HostPinnacle account
2. Navigate to the dashboard

## Step 3: Create a New Application

1. Click on "Create New App" or similar button
2. Choose a name for your application (e.g., "barberian")
3. Select the region closest to your target audience
4. Click "Create App"

## Step 4: Configure Database

1. Go to the "Resources" tab
2. Add a PostgreSQL database add-on
3. Choose a plan that fits your needs
4. Note the database credentials provided

## Step 5: Configure Environment Variables

1. Go to the "Settings" tab
2. Click on "Reveal Config Vars" or similar
3. Add the following environment variables based on your `.env.example` file:
   - `DEBUG`: Set to `False`
   - `SECRET_KEY`: Generate a secure random key
   - `ALLOWED_HOSTS`: Add your app's domain (e.g., `yourdomain.com,www.yourdomain.com`)
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

## Step 6: Deploy Your Application

1. Go to the "Deploy" tab
2. Connect your GitHub repository
3. Choose the branch you want to deploy (usually `main` or `master`)
4. Click "Deploy Branch"

## Step 7: Run Migrations

After deployment, you need to run migrations to set up your database:

1. Go to the "More" dropdown menu
2. Select "Run Console" or similar
3. Run the following command:
   ```
   python manage.py migrate
   ```

## Step 8: Create a Superuser

Create an admin user to access the Django admin panel:

1. Go to the "More" dropdown menu
2. Select "Run Console" or similar
3. Run the following command:
   ```
   python manage.py createsuperuser
   ```
4. Follow the prompts to create a superuser

## Step 9: Verify Deployment

1. Click on "Open App" to view your deployed application
2. Navigate to `/admin/` to access the Django admin panel
3. Log in with the superuser credentials you created

## Troubleshooting

If you encounter any issues during deployment, check the logs:

1. Go to the "More" dropdown menu
2. Select "View Logs" or similar
3. Look for error messages that might help identify the problem

Common issues:
- Missing environment variables
- Database connection problems
- Static files not being served correctly

## Maintenance

To update your application:

1. Push changes to your GitHub repository
2. Go to the "Deploy" tab
3. Click "Deploy Branch" again

You can also enable automatic deployments to deploy changes automatically when you push to your repository.
