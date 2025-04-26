# Barberian Deployment Guide for HostPinnacle

This guide provides detailed, step-by-step instructions for deploying the Barberian application to HostPinnacle.

## Prerequisites

Before you begin, make sure you have:

1. A HostPinnacle account
2. The deployment package (`barberian_hostpinnacle_deployment_YYYYMMDD.zip`)
3. Access to your domain's DNS settings (if you're using a custom domain)

## Step 1: Sign Up for HostPinnacle

If you don't already have a HostPinnacle account:

1. Go to [HostPinnacle's website](https://hostpinnacle.com/)
2. Click "Sign Up" or "Get Started"
3. Follow the registration process
4. Verify your email address

## Step 2: Create a New Application

1. Log in to your HostPinnacle dashboard
2. Click "Create New App" or a similar button
3. Choose a name for your application (e.g., "barberian")
4. Select the region closest to your target audience
5. Click "Create App"

## Step 3: Set Up Database

1. Go to the "Resources" tab in your HostPinnacle dashboard
2. Add a PostgreSQL database add-on
3. Choose a plan that fits your needs
4. Note the database credentials provided (you'll need these for environment variables)

## Step 4: Upload Your Application

There are two ways to deploy your application to HostPinnacle:

### Option 1: Deploy from GitHub

If your code is on GitHub:

1. Go to the "Deploy" tab
2. Choose "GitHub" as the deployment method
3. Connect your GitHub account
4. Search for and select your repository
5. Choose the branch you want to deploy (usually `main` or `master`)
6. Click "Deploy Branch"

### Option 2: Upload Deployment Package

If you're using the deployment package:

1. Go to the "Deploy" tab
2. Choose "Upload" or "Manual Deploy" as the deployment method
3. Upload the `barberian_hostpinnacle_deployment_YYYYMMDD.zip` file
4. Follow the prompts to complete the upload

## Step 5: Configure Environment Variables

1. Go to the "Settings" tab
2. Click "Reveal Config Vars" or a similar button
3. Add the following environment variables:

   ```
   DEBUG=False
   SECRET_KEY=your_secure_random_key
   ALLOWED_HOSTS=your-app-name.hostpinnacle.com,yourdomain.com
   
   # Database settings (use the values provided by HostPinnacle)
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=your_db_host
   DB_PORT=5432
   
   # Email settings
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.yourmailprovider.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your_email@yourdomain.com
   EMAIL_HOST_PASSWORD=your_email_password
   
   # Stripe settings (if applicable)
   STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
   STRIPE_SECRET_KEY=your_stripe_secret_key
   ```

   Replace the placeholder values with your actual values.

## Step 6: Run Migrations

After deployment, you need to run migrations to set up your database:

1. Go to the "More" dropdown menu
2. Select "Run Console" or a similar option
3. Run the following command:
   ```
   python manage.py migrate
   ```

## Step 7: Create a Superuser

Create an admin user to access the Django admin panel:

1. Go to the "More" dropdown menu
2. Select "Run Console" or a similar option
3. Run the following command:
   ```
   python manage.py createsuperuser
   ```
4. Follow the prompts to create a superuser

## Step 8: Collect Static Files (if needed)

If static files are not being served correctly:

1. Go to the "More" dropdown menu
2. Select "Run Console" or a similar option
3. Run the following command:
   ```
   python manage.py collectstatic --noinput
   ```

## Step 9: Set Up Custom Domain (Optional)

If you want to use your own domain:

1. Go to the "Settings" tab
2. Scroll to the "Domains" section
3. Click "Add Domain"
4. Enter your domain name (e.g., "barberian.com")
5. Follow the instructions to configure your DNS settings

## Step 10: Verify Deployment

1. Click "Open App" to view your deployed application
2. Navigate to `/admin/` to access the Django admin panel
3. Log in with the superuser credentials you created
4. Test the following functionality:
   - User registration and login
   - Appointment booking
   - Service browsing
   - Admin panel access

## Troubleshooting

If you encounter any issues during deployment, check the logs:

1. Go to the "More" dropdown menu
2. Select "View Logs" or a similar option
3. Look for error messages that might help identify the problem

Common issues:

- **Missing environment variables**: Make sure all required environment variables are set correctly.
- **Database connection problems**: Verify your database credentials and connection settings.
- **Static files not being served**: Run `collectstatic` and check your `STATIC_URL` and `STATICFILES_STORAGE` settings.
- **Application errors**: Check the application logs for specific error messages.

## Maintenance

To update your application:

1. Make changes to your code locally
2. Run tests to ensure everything works
3. Create a new deployment package or push to GitHub
4. Deploy the updated code to HostPinnacle

Regular maintenance tasks:

- Monitor application performance
- Regularly backup the database
- Keep dependencies updated
- Monitor error logs
- Apply security patches as needed

## Support

If you need help with your HostPinnacle deployment, you can:

1. Contact HostPinnacle support
2. Check the HostPinnacle documentation
3. Refer to the Django deployment documentation
4. Contact the Barberian development team
