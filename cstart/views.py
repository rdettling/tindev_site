from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from .models import Candidate
from rstart.models import JobPosting, JobInteraction, JobOffer
import string

# current logged-in candidate
currentCandidate = None

# filters for dashboard
active_filter = False
inactive_filter = False
city_filter = ""
state_filter = ""
keyword_filter = ""
keyword_string = ""

# homepage
def homepage(request):
    if(currentCandidate):
        redirect("signout")

    return render(request, "index.html")

# sign out of current candidate session
def signout(request):
    global currentCandidate
    global active_filter
    global inactive_filter
    global city_filter
    global state_filter
    global keyword_filter

    currentCandidate = None

    # disable any active filters
    active_filter = False
    inactive_filter = False
    city_filter = ""
    state_filter = ""
    keyword_filter = ""

    return redirect("/")

# new candidate creates an account
def signup(request):
    # on submit..
    if request.method == "POST":
        name = request.POST['name']
        bio = request.POST['bio']
        zipcode = request.POST['zipcode']
        skills = request.POST['skills']
        github = request.POST['github']
        years = request.POST['years']
        education = request.POST['education']
        username = request.POST['username']
        password = request.POST['password']

        # creates new object with all the inputted information
        new_candidate = Candidate.objects.create(name=name, bio=bio, zipcode=zipcode, skills=skills, github=github, years=years, education=education, username=username, password=password)
        new_candidate.save()

        # print('Successfully created new candidate account')

        return redirect("/")

    return render(request, "tindev_site/candidate/signup.html")

# allow existing candidate user to sign in
def signin(request):
    global currentCandidate

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # check if username exists
        if Candidate.objects.filter(username=username).exists():
            # if it does, check if password matches
            entry = Candidate.objects.filter(username=username)[0]

            if entry.password == password:

                currentCandidate = entry

                # print(entry.name)

                return redirect("/candidate/dashboard/")

    return render(request, "tindev_site/candidate/signin.html")

# handles the data for the candidate dashboard
def candidate_dashboard(request):
    global currentCandidate
    global active_filter
    global inactive_filter
    global city_filter
    global state_filter
    global keyword_filter
    global keyword_string

    # if we're logged in,
    if currentCandidate:
        # get relevant data from database; active job posts (unexpiry is checked in-template) and all of candidate's interactions
        current_job_postings = None

        if active_filter and inactive_filter:
            current_job_postings = list()
        elif active_filter:
            current_job_postings = list(JobPosting.objects.filter(status=True))
        elif inactive_filter:
            current_job_postings = list(JobPosting.objects.filter(status=False))
        else:
            current_job_postings = list(JobPosting.objects.filter())

        my_interactions = JobInteraction.objects.filter(candidate=currentCandidate.id)

        my_offers = JobOffer.objects.filter(candidate=currentCandidate.id)
        # offer = None
        # if len(my_offers):
        #     offer = my_offers[0].__dict__

        # this list holds the data for job postings, which will be a combination of the posting data and interest status
        postings = list()

        # filter and add all passing job postings in dict format, rather than JobPosting objects. 
        for job in current_job_postings:
            job_as_dict = job.__dict__

            visible = True 

            # if the city filter is active and this job isn't in that city, it doesn't pass the filtering, so break.
            if(city_filter != ""):
                print('test', job_as_dict['city'].lower(), city_filter.lower())
                if(not job_as_dict['city'].lower() == city_filter.lower()):
                    visible = False
            
            # if the state filter is active and this job isn't in that state, it doesn't pass the filtering, so break.
            if(state_filter != "" and visible):
                if(not job_as_dict['state'].lower() == state_filter.lower()):
                    visible = False

            # if the job skills doesn't contain any of the keywords, it doesn't pass the filtering, so break
            if(keyword_filter and visible):
                passes = False
                for word in [word.strip(string.punctuation) for word in job_as_dict['skills'].split()]:
                    if word.lower() in keyword_filter:
                        passes = True
                        break
                if not passes:
                    visible = False

            job_as_dict['offered'] = False
            if(len(my_offers)):
                for offer in my_offers:
                    offer_as_dict = offer.__dict__
                    if offer_as_dict['job'] == job_as_dict['id']:
                        if(offer_as_dict['accepted']):
                            job_as_dict['offered'] = "accepted"
                        else:
                            job_as_dict['offered'] = True
                        break

            if visible:
                postings.append(job_as_dict)

        # find matches in interest and job postings. Set a string on ['interested'] for in-template comparisons
        for job in postings:
            for interaction in my_interactions.values():
                if(job['id'] == interaction['job']):
                    if(interaction['interested']):
                        job['interested'] = 'Yes'
                    else:
                        job['interested'] = 'No'

        # add the string for the jobs that had no interest matches to indicate such
        for job in postings:
            if(not job['interested']):
                job['interested'] = 'None'

        # pass relevant data to the template to be rendered
        return render(request, "tindev_site/candidate/dashboard.html", {'currentCandidate': currentCandidate, 'current_job_postings': postings, 'active_filter': active_filter, 'inactive_filter': inactive_filter, 'city_filter': city_filter, 'state_filter': state_filter, 'keyword_filter': keyword_filter, 'keyword_string': keyword_string,})
    else:
        return redirect("/")

# allows candidate to mark interest/disinterest in a job
def mark_interest(request, job_id, candidate_id, interest):

    # convert to url-parsed string to boolean
    interest = eval(interest)

    # try to see if it exists before updating or creating
    try:
        JobInteraction.objects.get(job=job_id, candidate=candidate_id)
    except:
        # doesn't exist, so create a new interaction
        JobInteraction.objects.create(job=job_id, candidate=candidate_id, interested=interest)
    else:
        # does exist, so update the interested field of the interaction that already exists
        interaction = JobInteraction.objects.get(job=job_id, candidate=candidate_id)
        interaction.interested = interest
        interaction.save(update_fields=['interested'])

    return redirect("/candidate/dashboard/")

# allows candidate to mark accept/reject a job offer
def accept_offer(request, job_id, candidate_id, choice):
    # find the offer being acted upon
    offer = JobOffer.objects.get(job = job_id, candidate = candidate_id)
    interaction = JobInteraction.objects.get(job=job_id, candidate=candidate_id)
    job = JobPosting.objects.get(id = job_id)

    # convert string choice to boolean
    choice = eval(choice)

    # if choice is accept
    if(choice):
        offer.accepted = choice
        offer.save(update_fields=['accepted'])

        job.candidate = candidate_id
        job.save(update_fields=['candidate'])
    else:
        # we delete both the interaction and the offer, so its like new for both sides
        interation.delete()
        offer.delete()

    return redirect("/candidate/dashboard/")

# switches the active filter on/off
def active_toggle(request):
    global active_filter
    # toggles to opposite of current value
    active_filter = not active_filter
    return redirect("/candidate/dashboard/")

# switches the inactive filter on/off
def inactive_toggle(request):
    global inactive_filter
    # toggles to opposite of current value
    inactive_filter = not inactive_filter
    return redirect("/candidate/dashboard/")

# set the city filter to user's input
def city_toggle(request):
    global city_filter
    city = request.GET['city_filter']
    city_filter = city
    return redirect("/candidate/dashboard/")    

# set the state filter to user's input
def state_toggle(request):
    global state_filter
    state = request.GET['state_filter']
    state_filter = state
    return redirect("/candidate/dashboard/")

# set the keywords filter to user's input
def keyword_toggle(request):
    global keyword_filter
    global keyword_string
    keywords = request.GET['keyword_filter']

    # reset the set to empty on each use
    keyword_filter = set()
    for word in keywords.split():
        keyword_filter.add(word.lower())
    
    # create the display string of the current keywords
    keyword_string = ' '.join(keyword_filter)

    return redirect("/candidate/dashboard/")

# resets all filters to be disabled
def reset_filters(request):
    # global active_filter
    global city_filter
    global state_filter
    global keyword_filter

    # active_filter = None
    city_filter = ""
    state_filter = ""
    keyword_filter = ""

    return redirect("/candidate/dashboard/")