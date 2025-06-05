<?php
require_once "../includes/auth.php";

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $user = $_POST["username"] ?? "";
    $pass = $_POST["password"] ?? "";
    if (login($user, $pass)) {
        echo "Login successful!";
    } else {
        echo "Login failed.";
    }
} else {
?>
<form method="POST">
    <input type="text" name="username" placeholder="User" required>
    <input type="password" name="password" placeholder="Password" required>
    <input type="submit" value="Login">
</form>
<?php
}
?>
