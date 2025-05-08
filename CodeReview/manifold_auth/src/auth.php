<?php
require 'vendor/autoload.php';
use Firebase\JWT\JWT;

$key = "secret";
$jwt = $_GET["token"] ?? "";

if ($jwt) {
    try {
        $decoded = JWT::decode($jwt, $key, array('HS256'));
        echo "Welcome " . $decoded->user;
    } catch (Exception $e) {
        echo "Invalid token.";
    }
} else {
    echo "No token provided.";
}
?>
