import uuid

# Mock Employee Database
MOCK_EMPLOYEE_DB = {
    "Jane Doe": {
        "email": "jane.doe@company.com",
        "annual_leave": 18,
        "sick_leave": 6,
        "unpaid_leave": 10
    },
    "Alice Smith": {
        "email": "alice.smith@company.com",
        "annual_leave": 14,
        "sick_leave": 5,
        "unpaid_leave": 12
    },
    "Bob Jones": {
        "email": "bob.jones@company.com",
        "annual_leave": 8,
        "sick_leave": 3,
        "unpaid_leave": 5
    }
}

def handle_password_reset(ticket_text: str, user_email: str = "jane.doe@company.com") -> dict:
    """
    Simulates checking the user database, generating a secure reset token, and drafting instructions.
    """
    # Simulate API call / security token generation
    reset_token = str(uuid.uuid4())[:18]
    reset_url = f"https://identity.company.com/reset-password?token={reset_token}"
    
    response_text = f"""### 🔐 Password Reset Instructions

Hello,

It looks like you are having trouble logging in or need to reset your password. 

We have generated a secure password reset link for your account associated with **{user_email}**:

👉 **[Click here to reset your password]({reset_url})**

*Note: For security reasons, this link is single-use and will expire in 15 minutes. If you did not request this, please contact the IT Security team immediately.*

Best regards,  
**IT Support Automation**"""
    
    return {
        "action_taken": f"Generated secure SSPR token: {reset_token} for {user_email}",
        "response_md": response_text,
        "status": "Resolved"
    }

def handle_leave_balance(ticket_text: str, employee_name: str = "Jane Doe") -> dict:
    """
    Queries the mock HR database for leave balance and drafts a response.
    """
    employee_data = MOCK_EMPLOYEE_DB.get(employee_name, MOCK_EMPLOYEE_DB["Jane Doe"])
    
    response_text = f"""### 📅 Leave Balance Summary

Hello {employee_name},

Here is the current summary of your leave balances retrieved from the HR Information System (HRIS):

*   **Annual Leave (Vacation):** **{employee_data['annual_leave']} days** remaining
*   **Sick Leave:** **{employee_data['sick_leave']} days** remaining
*   **Unpaid Leave:** **{employee_data['unpaid_leave']} days** remaining

To request time off or plan your vacation, please submit a request through the **[HR Portal](https://hr.company.com/timeoff)**.

Best regards,  
**HR Self-Service Assistant**"""
    
    return {
        "action_taken": f"Queried HRIS database for '{employee_name}' (Email: {employee_data['email']})",
        "response_md": response_text,
        "status": "Resolved"
    }

def handle_human_escalation(ticket_text: str) -> dict:
    """
    Handles fallback tickets by creating a mock ticket and routing to support queue.
    """
    ticket_id = f"TIC-{uuid.uuid4().hex[:6].upper()}"
    
    response_text = f"""### ⚙️ Ticket Escalation Notice

Hello,

We received your request:  
*" {ticket_text} "*

This topic requires assistance from a human support specialist. We have automatically created a high-priority ticket for you:

🎫 **Ticket ID:** `{ticket_id}`  
📂 **Status:** `Assigned to Support Queue`

An IT or HR engineer will review your issue and follow up with you shortly. You can track progress or add comments in the IT Helpdesk Portal.

Best regards,  
**Helpdesk Router**"""
    
    return {
        "action_taken": f"Created support ticket {ticket_id} and assigned to general queue.",
        "response_md": response_text,
        "status": "Escalated"
    }

def resolve_ticket(category: str, ticket_text: str, employee_name: str = "Jane Doe") -> dict:
    """
    Routes the ticket category to the correct resolver function.
    """
    if category == "password_issue":
        email = MOCK_EMPLOYEE_DB.get(employee_name, {}).get("email", "user@company.com")
        return handle_password_reset(ticket_text, email)
    elif category == "leave_issue":
        return handle_leave_balance(ticket_text, employee_name)
    else:
        return handle_human_escalation(ticket_text)
