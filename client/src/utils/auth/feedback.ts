import { AuthFailure } from "@services/http/validate";

export const authFeedback = (error: unknown): string => {
  if (error instanceof AuthFailure) {
    switch (error.code) {
      case "INVALID_CREDENTIALS":
        return "The email or password is invalid. Check your credentials and try again.";
      case "VERIFICATION_REQUIRED":
        return "Verify your account before signing in. Enter your email and code on Verify account.";
      case "ACCOUNT_ALREADY_EXISTS":
        return "An account already exists for this email. If you still need verification, visit Verify account.";
      case "INVALID_VERIFICATION":
        return "The verification code is invalid. Check your email and code, or request another code.";
      case "VERIFICATION_EXPIRED":
        return "The verification code has expired. Request another code.";
      case "VERIFICATION_NOT_REQUIRED":
        return "This account does not require verification.";
      case "ACCOUNT_NOT_FOUND":
        return "No account was found for this email. Check the email or register an account.";
      case "UNPROCESSABLE_ENTITY":
        return "Check the form values and try again.";
      case "REQUEST_PENDING":
        return "A request is already in progress. Please wait.";
      default:
        return "The request could not be confirmed. Please try again.";
    }
  } else {
    return "The request could not be confirmed. Please try again.";
  }
};
