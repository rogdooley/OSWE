package com.vanadium.forms;

import javax.servlet.*;
import javax.servlet.http.*;
import java.io.*;

public class FormUploadServlet extends HttpServlet {
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
        try {
            Object obj = ois.readObject();
            response.getWriter().write("Received form object: " + obj.toString());
        } catch (Exception e) {
            response.getWriter().write("Invalid data.");
        } finally {
            ois.close();
        }
    }
}
