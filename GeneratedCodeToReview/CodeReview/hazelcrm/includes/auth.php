<?php
function auth($user, $pass) {
    $creds = [
        ["user" => "admin", "pass" => "secure123"],
        ["user" => "guest", "pass" => "guest"]
    ];

    foreach ($creds as $entry) {
        if ($entry["user"] == $user && $entry["pass"] == $pass) {
            return true;
        }
    }

    return false;
}
?>
