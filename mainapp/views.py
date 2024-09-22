from django.shortcuts import render
from django.http import HttpResponseNotFound
# Create your views here.
import json


# Load data from the JSON file
def load_courses_data():
    with open('media/get_all_courses_API_response.json') as f:
        return json.load(f)

def course_list(request):
    data = load_courses_data()
    courses = data.get('courses', [])
    facets = data.get('facets', {})

    # If filters are applied
    selected_facets = {
        'language': request.GET.get('language', None),
        'duration': request.GET.get('duration', None),
        'subject': request.GET.get('subject', None),
         'search_query': request.GET.get('search_query', '').strip(),
    }

    # Apply filters to courses
    filtered_courses = courses
    if selected_facets['language']:
        filtered_courses = [course for course in filtered_courses if course['course_language'].lower() == selected_facets['language'].lower()]

    if selected_facets['duration']:
        filtered_courses = [course for course in filtered_courses if course['course_duration'] == selected_facets['duration']]

    if selected_facets['subject']:
        filtered_courses = [course for course in filtered_courses if course['course_subject'].lower() == selected_facets['subject'].lower()]
        
    if selected_facets['search_query']:
        filtered_courses = [
            course for course in filtered_courses 
            if selected_facets['search_query'].lower() in course['course_name'].lower() or
               selected_facets['search_query'].lower() in course.get('course_description', '').lower()  # Optional description filter
        ]    
       
    
    print(filtered_courses)  
    
    
    return render(request, 'course_list.html', {
        'courses': filtered_courses,
        'facets': facets,
        'selected_facets': selected_facets,
    })



def convert_to_embed(youtube_url):
  

    if 'v=' in youtube_url:
        video_id = youtube_url.split('v=')[-1].split('&')[0]  # Get the video ID
    elif 'youtu.be/' in youtube_url:
        video_id = youtube_url.split('youtu.be/')[-1].split('?')[0]  # Handle shortened URLs
    else:
        return None  # Invalid URL format

    return f'https://www.youtube.com/embed/{video_id}'


def course_detail(request, course_id):
    # Load course data
    course_data = load_course_detail_data(course_id)
    if not course_data:
        return HttpResponseNotFound('Course not found')

    video_id = request.GET.get('video_id')
    selected_video = next(
        (video for video in course_data.get('videos', []) if video['video_id'] == video_id),
        course_data.get('videos', [])[0] if course_data.get('videos') else None
    )

    # Modify the youtube_url to embed format if selected_video is a dictionary
    if selected_video and 'youtube_url' in selected_video:
        selected_video['youtube_url'] = convert_to_embed(selected_video['youtube_url'])

    context = {
        'course': course_data,
        'videos': course_data.get('videos', []),
        'selected_video': selected_video
    }

    return render(request, 'course_detail.html', context)


    
def load_course_detail_data(course_id):
    with open('media/get_course_detail_API_response.json') as f:
        return json.load(f)
  