<?php
session_start();
$csrf_token = bin2hex(random_bytes(16));
$_SESSION['csrf_token'] = $csrf_token;
?>

<form method="POST" action="submit.php">
    <input type="hidden" name="csrf" value="<?php echo $csrf_token; ?>" />
    <textarea name="payload" rows="6" cols="60">a:1:{s:4:"user";s:5:"guest";}</textarea><br>
    <input type="submit" value="Submit">
</form>
