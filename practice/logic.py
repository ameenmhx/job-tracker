def get_status(count):
    if count==0:
        return "no job"
    elif count < 5:
        return "part-time"
    else:
        return "full-time"
    
status = get_status(3)
print(status)


job = {
   "company": "google",
   "status": "applied"
}

print (job["company"])