<?php
session_start();
$token = $_SESSION["id_token"] ?? "none";

if ($token === "admin-token") {
    echo "Welcome, admin!";
} else {
    echo "User page.";
}
