<?php
$host = getenv('DATABASE_HOST') ?: '127.0.0.1';
$db   = getenv('DATABASE_NAME') ?: 'test_db';
$user = 'web';
$pass = getenv('WEB_PASSWORD') ?: 'test';
$charset = 'utf8';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    die('Error al conectar a la base de datos: ' . $e->getMessage());
}
?>
