package com.solstice.accounts;

import org.springframework.web.bind.annotation.*;
import java.sql.*;

@RestController
public class UserController {

    @GetMapping("/user")
    public String getUser(@RequestParam String id) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:postgresql://localhost:5432/solstice", "user", "pass");
            Statement stmt = conn.createStatement();
            String query = "SELECT * FROM users WHERE id = '" + id + "'";
            ResultSet rs = stmt.executeQuery(query);
            if (rs.next()) {
                return "User: " + rs.getString("name");
            }
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
        return "User not found.";
    }
}
