from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from .models import Recruiter, JobPosting, JobInteraction, JobOffer
from cstart.models import Candidate
from django.urls import reverse

# current logged-in recruiter
currentRecruiter = None
currentCompany = None

# filters for dashboard
active_filter = None
inactive_filter = None
interest_filter = None

# functions (views) for all of the urls
def homepage(request):
    global currentRecruiter

    if(currentRecruiter):
        redirect("/signout")

    return render(request, "index.html")

# signs out of current 'session'
def signout(request):
    global currentRecruiter
    global currentCompany
    currentRecruiter = None
    currentCompany = None

    return redirect("/")

# new recruiter creates an account
def signup(request):
    # on submit
    if request.method == "POST":
        name = request.POST['name']
        company = request.POST['company']
        zipcode = request.POST['zipcode']
        username = request.POST['username']
        password = request.POST['password']

        # create new recruiter object with inputted data
        new_recruiter = Recruiter.objects.create(name=name, company=company, zipcode=zipcode, username=username, password=password)
        new_recruiter.save()

        return redirect("/")

    return render(request, "tindev_site/recruiter/signup.html")


# allow existing recruiter user to sign in
def signin(request):
    global currentRecruiter
    global currentCompany

    # on signin
    if request.method == 'POST':
        # get input
        username = request.POST['username']
        password = request.POST['password']

        # check if username exists
        if Recruiter.objects.filter(username=username).exists():
            entry = Recruiter.objects.filter(username=username)[0]
            # if it does, check if password matches
            if entry.password == password:
                # create 'session' by storing current recruiter and company
                currentRecruiter = entry.username
                currentCompany = entry.company

                return redirect("/recruiter/dashboard/")

    return render(request, "tindev_site/recruiter/signin.html")

# handles the data for the recruiter dashboard view
def recruiter_dashboard(request):
    global currentRecruiter
    global active_filter
    global inactive_filter
    global interest_filter

    # check that a recruiter is logged in before trying to dashboard
    if currentRecruiter:

        # These are all the possible combos of filters
        if(active_filter and inactive_filter):
            # these cancel eachother out; you cant be active and inactive
            my_job_postings = []
        elif(active_filter):
            my_job_postings = JobPosting.objects.filter(recruiter=currentRecruiter, status=1)
        elif(inactive_filter):
            my_job_postings = JobPosting.objects.filter(recruiter=currentRecruiter, status=0)
        else:
            # else just give all the jobs
            my_job_postings = JobPosting.objects.filter(recruiter=currentRecruiter)

        if(interest_filter):
            temp_jobs = []
            for job in my_job_postings:
                if(job.num_interested() > 0):
                    temp_jobs.append(job)
            my_job_postings = temp_jobs


        return render(request, "tindev_site/recruiter/dashboard.html", {
            'currentRecruiter': currentRecruiter, 
            'my_job_postings': my_job_postings, 
            'active_filter': active_filter, 
            'inactive_filter': inactive_filter, 
            'interest_filter': interest_filter,
            })
    else:
        return redirect("/")

# switches the active filter on/off
def active_toggle(request):
    global active_filter
    # toggles to opposite of current value
    active_filter = not active_filter
    return redirect("/recruiter/dashboard/")

# switches the inactive filter on/off
def inactive_toggle(request):
    global inactive_filter
    # toggles to opposite of current value
    inactive_filter = not inactive_filter
    return redirect("/recruiter/dashboard/")

# switches the interest filter on/off
def interest_toggle(request):
    global interest_filter
    # toggles to opposite of current value
    interest_filter = not interest_filter
    return redirect("/recruiter/dashboard/")

# creates a new job with form fields on post
def create_job(request):
    global currentRecruiter
    global currentCompany

    # if we submit and we're logged in
    if request.method == "POST" and currentRecruiter and currentCompany:
        position = request.POST['position']
        postype = request.POST['postype']
        city = request.POST['city']
        state = request.POST['state']
        skills = request.POST['skills']
        expiration = request.POST['expiration']
        status = request.POST['status']

        # recruiter and company come from login session globals
        new_job_posting = JobPosting.objects.create(
            recruiter=currentRecruiter,
            company=currentCompany,
            position=position,
            postype=postype,
            city=city,
            state=state,
            skills=skills,
            expiration=expiration,
            status=status,
            )
        new_job_posting.save()

        # return to dashboard
        return redirect("/recruiter/dashboard/")

    return render(request, "tindev_site/recruiter/create_job.html")

# updates an already existing job
def update_job(request, job_id):
    # ids are unique, so filter to the inputted id and take the first of the set
    job = JobPosting.objects.get(id=job_id)

    # when population the date form, it needs to be in this format or else it doesn't get accepted as a value
    expiration_str = job.expiration.strftime("%Y-%m-%d")

    # on submit...
    if request.method == "POST":
        # update the fields to whatever they now hold
        JobPosting.objects.filter(id=job_id).update(
            position = request.POST['position'],
            postype = request.POST['postype'],
            city = request.POST['city'],
            state = request.POST['state'],
            skills = request.POST['skills'],
            expiration = request.POST['expiration'],
            status = request.POST['status'],
        )
        # return to dashboard
        return redirect("/recruiter/dashboard/")

    return render(request, "tindev_site/recruiter/update_job.html", {"job": job, "expiration_str": expiration_str})

# deletes a job posting
def delete_job(request, job_id):
    # easy enough
    JobPosting.objects.filter(id=job_id).delete()
    return redirect("/recruiter/dashboard/")

# handles the data for the job details view
def job_details(request, job_id):
    # get the details of the job for displaying
    job = JobPosting.objects.get(id=job_id)

    # get all interested interactions
    interactions = JobInteraction.objects.filter(job=job_id, interested=True)

    # get associated job offer, if it exists
    offer = JobOffer.objects.filter(job=job_id)
    
    # create a list of the candidates who interacted with interest
    candidates = list()
    for i in interactions:
        # get the cand id of the assc interaction, convert to dict, and add to list
        candidates.append(Candidate.objects.get(id=i.candidate).__dict__)

    for c in candidates:
        # for each candidate, calculate a compatibility score between 1 and 3
        cskills = set([skill.lower() for skill in c['skills'].split(' ')])
        jskills = set([skill.lower() for skill in job.__dict__['skills'].split(' ')])

        score = 0

        # if they share a bio skill and job skill, add a point
        for skill in cskills:
            if skill in jskills:
                score += 1

        # give the candidate dict its score ranges for later display
        if score <= 0:
            c['score'] = 1
        elif score > 0 and score < 3:
            c['score'] = 2
        else:
            c['score'] = 3

        # while we're here iterating, we can check if its the candidate of the job offer
        if offer and offer[0].__dict__['candidate'] == c['id']:
            c['offer'] = True
            if offer[0].__dict__['accepted']:
                c['accepted'] = True
        else:
            c['offer'] = False

    return render(request, "tindev_site/recruiter/job_details.html", {"job": job, "candidates": candidates,})

# sends a job offer to the chosen candidate
def offer_job(request, job_id, candidate_id):
    try: # see if this job has been offerred to anyone yet
        JobOffer.objects.get(job=job_id)
    except: # if not, make a new offer instance for this job and the selected candidate
        JobOffer.objects.create(job=job_id, candidate=candidate_id)
    else: # does exist, so update to the new candidate if it hadn't been accepted
        offer = JobOffer.objects.get(job=job_id)
        if not offer.accepted:
            offer.candidate = candidate_id
            offer.save(update_fields=['candidate'])

    return redirect("/recruiter/job_details/"+job_id)