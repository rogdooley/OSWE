package com.orbitportal;

import org.springframework.web.bind.annotation.*;
import javax.servlet.http.*;

@RestController
public class UserController {

    @GetMapping("/login")
    public String login(@RequestParam String user, HttpServletResponse response) {
        Cookie cookie = new Cookie("session", user);
        cookie.setPath("/");
        response.addCookie(cookie);
        return "Logged in as " + user;
    }

    @GetMapping("/dashboard")
    public String dashboard(@CookieValue(value = "session", defaultValue = "guest") String session) {
        if ("admin".equals(session)) {
            return "<h1>Admin Dashboard</h1><p>Welcome back, admin!</p>";
        } else {
            return "<h1>User Dashboard</h1><p>Hello, " + session + "</p>";
        }
    }

    @PostMapping("/feedback")
    public String postFeedback(@RequestParam String comment, @CookieValue(value = "session", defaultValue = "guest") String session) {
        return "Thanks " + session + "! We received: " + comment;
    }

    @GetMapping("/admin/reports")
    public String viewFeedback(@RequestParam(required = false) String data) {
        return "<h1>Reports</h1><p>" + data + "</p>";
    }
}
