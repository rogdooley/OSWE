<?php
session_start();
$id_token = $_GET["id_token"] ?? "";

if ($id_token) {
    $_SESSION["id_token"] = $id_token;
    echo "Logged in with token: " . htmlspecialchars($id_token);
} else {
    echo "No token.";
}
