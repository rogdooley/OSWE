<?php
function login($username, $password) {
    $users = [
        "admin" => ["password" => "secret123", "role" => "admin"],
        "user" => ["password" => "userpass", "role" => "user"]
    ];
    if (!isset($users[$username])) {
        return false;
    }
    return $users[$username]["password"] == $password;
}
?>
