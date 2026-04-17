from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from jobs.models import Job

def recommend_jobs(profile, top_n=10):
    if not profile.search_vector:
        return []

    # Get all active jobs that have a search vector
    jobs = Job.objects.filter(is_active=True).exclude(search_vector__isnull=True).exclude(search_vector__exact='')
    if not jobs.exists():
        return []

    job_list = list(jobs)
    job_vectors = [job.search_vector for job in job_list]
    
    # Add profile vector as the first element for comparison
    documents = [profile.search_vector] + job_vectors
    
    # Calculate TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return []

    # Calculate cosine similarity of profile (index 0) with all jobs (index 1 to N)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Get top matching indices
    top_indices = cosine_sim.argsort()[::-1][:top_n]
    
    # Filter out jobs with negligible similarity
    recommended_jobs = []
    for i in top_indices:
        if cosine_sim[i] > 0.01: # base threshold
            # Assign a similarity score attribute to the job object dynamically
            job = job_list[i]
            job.similarity_score = round(cosine_sim[i] * 100, 2)
            recommended_jobs.append(job)
            
    return recommended_jobs
