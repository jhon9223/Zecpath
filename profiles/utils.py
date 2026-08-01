from accounts.models import User


def get_user_profile(user):
    if user.role == User.CANDIDATE:
        return user.candidate_profile

    elif user.role == User.EMPLOYER:
        return user.employer_profile

    return None
# this function takes a user object as input and checks the user's role. If the role is CANDIDATE, it returns the associated CandidateProfile object. If the role is EMPLOYER, it returns the associated EmployerProfile object. If the role does not match either of these, it returns None.
# its a utility function that can be used throughout the application to retrieve the appropriate profile for a given user.
