jobs= [
  {
    "company": "google",
    "status": "applied",
   
  },
  {
    "company": "amazon",
    "status": "interviewing",
  },
  {
    "company": "facebook",
    "status": "hired",
  },
  {
    "company": "apple",
    "status": "rejected",
  }
]


for job in jobs:
    print(job["company"], "-", job["status"])

for job in jobs:
    if job["status"] =="hired":
        print("Congratulations! You got a job at", job["company"])

applied_count =0
for job in jobs:
        if job["status"] =="applied":
            applied_count +=1

print("total applied", applied_count)

def count_by_status(jobs, status):
    count = 0
    for job in jobs:
        if job["status"] == status:
            count += 1
    return count

print(count_by_status(jobs, "Applied"))
print(count_by_status(jobs, "Interview"))
