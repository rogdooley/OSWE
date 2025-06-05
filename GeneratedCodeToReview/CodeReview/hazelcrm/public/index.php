<?php
require_once "../includes/auth.php";

session_start();
if ($_SERVER["REQUEST_METHOD"] === "POST") {
    $user = $_POST["username"] ?? "";
    $pass = $_POST["password"] ?? "";
    if (auth($user, $pass)) {
        $_SESSION["auth"] = true;
        echo "Welcome, " . htmlspecialchars($user);
    } else {
        echo "Login failed.";
    }
} else {
?>
<form method="POST">
    <input name="username" />
    <input name="password" type="password" />
    <input type="submit" value="Login" />
</form>
<?php } ?>
