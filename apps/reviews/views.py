from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.utils import timezone

from .models import Review, ReviewResponse
from .forms import ReviewForm, ReviewResponseForm
from apps.appointments.models import Appointment
from apps.services.models import Service
from apps.core.models import User
from apps.notifications.models import Notification

def review_list(request):
    """
    View for listing reviews.
    """
    # Get all approved reviews
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')

    # Get average ratings
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()

    # Get top-rated staff
    top_staff = User.objects.filter(role='staff').annotate(
        avg_rating=Avg('staff_reviews__rating'),
        review_count=Count('staff_reviews')
    ).filter(review_count__gt=0).order_by('-avg_rating')[:5]

    # Get top-rated services
    top_services = Service.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gt=0).order_by('-avg_rating')[:5]

    return render(request, 'reviews/review_list.html', {
        'title': 'Reviews',
        'reviews': reviews,
        'average_rating': average_rating,
        'rating_distribution': rating_distribution,
        'top_staff': top_staff,
        'top_services': top_services,
    })

@login_required
def review_detail(request, review_id):
    """
    View for viewing a review.
    """
    # Get the review
    review = get_object_or_404(Review, id=review_id)

    # Check if the review is approved or if the user is the client or staff
    if not review.is_approved and request.user != review.client and request.user != review.staff and request.user.role != 'admin':
        messages.error(request, "You don't have permission to view this review.")
        return redirect('reviews:review_list')

    # Get the response form if the user is the staff or an admin
    response_form = None
    if request.user == review.staff or request.user.role == 'admin':
        response_form = ReviewResponseForm(request.POST or None, instance=getattr(review, 'response', None))

        if request.method == 'POST' and response_form.is_valid():
            response = response_form.save(commit=False)
            response.review = review
            response.staff = request.user
            response.save()

            # Create a notification for the client
            Notification.objects.create(
                user=review.client,
                type='review',
                title='Response to Your Review',
                message=f"{review.staff.get_full_name()} has responded to your review for {review.service.name}.",
                related_review=review
            )

            messages.success(request, "Your response has been saved.")
            return redirect('reviews:review_detail', review_id=review.id)

    return render(request, 'reviews/review_detail.html', {
        'title': 'Review Details',
        'review': review,
        'response_form': response_form,
    })

@login_required
def review_create(request, appointment_id=None):
    """
    View for creating a review.
    """
    # Check if the user is a client
    if request.user.role != 'client':
        messages.error(request, "Only clients can leave reviews.")
        return redirect('reviews:review_list')

    # Get the appointment if provided
    appointment = None
    if appointment_id:
        appointment = get_object_or_404(Appointment, id=appointment_id)

        # Check if the user is the client
        if request.user != appointment.client:
            messages.error(request, "You can only review your own appointments.")
            return redirect('reviews:review_list')

        # Check if the appointment is completed
        if appointment.status != 'completed':
            messages.error(request, "You can only review completed appointments.")
            return redirect('reviews:review_list')

        # Check if the appointment already has a review
        if hasattr(appointment, 'review'):
            messages.error(request, "You have already reviewed this appointment.")
            return redirect('reviews:review_detail', review_id=appointment.review.id)

    # Initialize the form
    form = ReviewForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.client = request.user

        if appointment:
            review.appointment = appointment
            review.service = appointment.service
            review.staff = appointment.staff
        else:
            # If no appointment, get the service and staff from the form
            service_id = request.POST.get('service')
            staff_id = request.POST.get('staff')

            if not service_id or not staff_id:
                messages.error(request, "Please select a service and staff member.")
                return redirect('reviews:review_create')

            review.service = get_object_or_404(Service, id=service_id)
            review.staff = get_object_or_404(User, id=staff_id, role='staff')

        # Set approval status based on settings (auto-approve or require moderation)
        # For now, we'll set it to require moderation
        review.is_approved = False

        review.save()

        # Create notifications
        Notification.objects.create(
            user=review.staff,
            type='review',
            title='New Review',
            message=f"{review.client.get_full_name()} has left a review for {review.service.name}.",
            related_review=review
        )

        # Notify admins
        for admin in User.objects.filter(role='admin'):
            Notification.objects.create(
                user=admin,
                type='review',
                title='New Review Needs Approval',
                message=f"{review.client.get_full_name()} has left a review for {review.service.name} that needs approval.",
                related_review=review
            )

        messages.success(request, "Your review has been submitted and is pending approval.")
        return redirect('reviews:my_reviews')

    # Get all services and staff for the form
    services = Service.objects.filter(is_active=True)
    staff = User.objects.filter(role='staff')

    return render(request, 'reviews/review_form.html', {
        'title': 'Leave a Review',
        'form': form,
        'appointment': appointment,
        'services': services,
        'staff': staff,
    })

@login_required
def review_edit(request, review_id):
    """
    View for editing a review.
    """
    # Get the review
    review = get_object_or_404(Review, id=review_id)

    # Check if the user is the client
    if request.user != review.client:
        messages.error(request, "You can only edit your own reviews.")
        return redirect('reviews:review_list')

    # Initialize the form
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)

        # Reset approval status if the review is edited
        review.is_approved = False

        review.save()

        # Create notifications
        Notification.objects.create(
            user=review.staff,
            type='review',
            title='Review Updated',
            message=f"{review.client.get_full_name()} has updated their review for {review.service.name}.",
            related_review=review
        )

        # Notify admins
        for admin in User.objects.filter(role='admin'):
            Notification.objects.create(
                user=admin,
                type='review',
                title='Updated Review Needs Approval',
                message=f"{review.client.get_full_name()} has updated their review for {review.service.name} that needs approval.",
                related_review=review
            )

        messages.success(request, "Your review has been updated and is pending approval.")
        return redirect('reviews:my_reviews')

    return render(request, 'reviews/review_form.html', {
        'title': 'Edit Review',
        'form': form,
        'review': review,
    })

@login_required
def review_delete(request, review_id):
    """
    View for deleting a review.
    """
    # Get the review
    review = get_object_or_404(Review, id=review_id)

    # Check if the user is the client or an admin
    if request.user != review.client and request.user.role != 'admin':
        messages.error(request, "You don't have permission to delete this review.")
        return redirect('reviews:review_list')

    if request.method == 'POST':
        # Delete the review
        review.delete()

        messages.success(request, "The review has been deleted.")

        # Redirect based on user role
        if request.user.role == 'admin':
            return redirect('admin_panel:reviews')
        else:
            return redirect('reviews:my_reviews')

    return render(request, 'reviews/review_delete.html', {
        'title': 'Delete Review',
        'review': review,
    })

@login_required
def my_reviews(request):
    """
    View for listing a client's reviews.
    """
    # Check if the user is a client
    if request.user.role != 'client':
        messages.error(request, "This page is only for clients.")
        return redirect('reviews:review_list')

    # Get the client's reviews
    reviews = Review.objects.filter(client=request.user).order_by('-created_at')

    # Get completed appointments without reviews
    appointments_without_reviews = Appointment.objects.filter(
        client=request.user,
        status='completed'
    ).exclude(
        id__in=Review.objects.filter(client=request.user).values_list('appointment_id', flat=True)
    ).order_by('-start_time')

    return render(request, 'reviews/my_reviews.html', {
        'title': 'My Reviews',
        'reviews': reviews,
        'appointments_without_reviews': appointments_without_reviews,
    })

def staff_reviews(request, staff_id=None):
    """
    View for listing reviews for a staff member.
    """
    # Get the staff member
    if staff_id:
        staff = get_object_or_404(User, id=staff_id, role='staff')
    elif request.user.is_authenticated and request.user.role == 'staff':
        staff = request.user
    else:
        messages.error(request, "Invalid staff member.")
        return redirect('reviews:review_list')

    # Get the staff's reviews
    reviews = Review.objects.filter(staff=staff, is_approved=True).order_by('-created_at')

    # Get average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()

    return render(request, 'reviews/staff_reviews.html', {
        'title': f'Reviews for {staff.get_full_name()}',
        'staff': staff,
        'reviews': reviews,
        'average_rating': average_rating,
        'rating_distribution': rating_distribution,
    })

def service_reviews(request, service_id):
    """
    View for listing reviews for a service.
    """
    # Get the service
    service = get_object_or_404(Service, id=service_id)

    # Get the service's reviews
    reviews = Review.objects.filter(service=service, is_approved=True).order_by('-created_at')

    # Get average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Get rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()

    return render(request, 'reviews/service_reviews.html', {
        'title': f'Reviews for {service.name}',
        'service': service,
        'reviews': reviews,
        'average_rating': average_rating,
        'rating_distribution': rating_distribution,
    })

@login_required
def admin_review_list(request):
    """
    View for listing all reviews for admin.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('reviews:review_list')

    # Get all reviews
    reviews = Review.objects.all().order_by('-created_at')

    # Filter by approval status if provided
    approval_status = request.GET.get('approval_status')
    if approval_status == 'approved':
        reviews = reviews.filter(is_approved=True)
    elif approval_status == 'pending':
        reviews = reviews.filter(is_approved=False)

    return render(request, 'reviews/admin_review_list.html', {
        'title': 'Manage Reviews',
        'reviews': reviews,
        'approval_status': approval_status,
    })

@login_required
def admin_review_approve(request, review_id):
    """
    View for approving a review.
    """
    # Check if the user is an admin
    if request.user.role != 'admin':
        messages.error(request, "You don't have permission to access this page.")
        return redirect('reviews:review_list')

    # Get the review
    review = get_object_or_404(Review, id=review_id)

    # Approve the review
    review.is_approved = True
    review.save()

    # Create a notification for the client
    Notification.objects.create(
        user=review.client,
        type='review',
        title='Review Approved',
        message=f"Your review for {review.service.name} has been approved and is now visible to others.",
        related_review=review
    )

    messages.success(request, "The review has been approved.")
    return redirect('admin_panel:reviews')
