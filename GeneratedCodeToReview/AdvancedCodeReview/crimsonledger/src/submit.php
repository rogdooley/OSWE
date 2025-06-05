<?php
session_start();
if ($_POST['csrf'] !== $_SESSION['csrf_token']) {
    die("CSRF check failed.");
}

$payload = $_POST['payload'];
$data = unserialize($payload);

$redis = new Redis();
$redis->connect('127.0.0.1', 6379);
$redis->set("user:" . $data['user'], "logged");

echo "Submitted for user: " . htmlspecialchars($data['user']);
