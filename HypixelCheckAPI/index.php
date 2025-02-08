<?php
require_once './SpelakoCore/SpelakoCore.php';

function processCommand($command, $userId) {
    $core = new SpelakoCore('config.json');
    return $core->execute($command, $userId);
}

function logRequest($ip, $command, $userId) {
    $date = date('Y-m-d H:i:s');
    $logMessage = "[$date] $ip | $command | User: $userId";
    error_log($logMessage);
}

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$clientIP = $_SERVER['REMOTE_ADDR'];

if ($method == 'GET' && $path == '/hypixel') {
    $command = $_GET['command'] ?? '';
    $userId = $_GET['userId'] ?? 'defaultUser';

    logRequest($clientIP, $command, $userId);

	$result = processCommand($command, $userId);

    header('Content-Type: application/json');
    echo json_encode($result);
} else {
    header('HTTP/1.0 405 Method Not Allowed');
    echo 'Method Not Allowed';
}
?>