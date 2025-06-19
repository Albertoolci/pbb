<?php
require 'db_config.php';

$tag = $_GET['tag'] ?? '';
$info = $_GET['info'] ?? '';
$table = getenv('TABLE_NAME') ?: 'votos';
// Generar consulta segura
$query = "SELECT * FROM $table WHERE 1=1";
$params = [];

if (!empty($tag)) {
    $query .= " AND tag = :tag";
    $params[':tag'] = trim(strtolower($tag));
}
if (!empty($info)) {
    $query .= " AND info = :info";
    $params[':info'] = trim(strtolower($info));;
}

$stmt = $pdo->prepare($query);
$stmt->execute($params);
$rows = $stmt->fetchAll();
$count = count($rows);
?>

<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Visor de Datos</title>
    <style>
        table { 
            border-collapse: collapse; 
            width: 100%; 
        }
        th, td { 
            border: 1px solid #ccc; 
            padding: 8px; 
            text-align: left; 
            white-space: nowrap; /* Evita que el texto se corte y obliga al desbordamiento */
        }
        th { 
            background-color: #eee; 
        }
        form { 
            margin-bottom: 20px; 
        }
        
        /* Contenedor con scroll horizontal */
        .table-container {
            overflow-x: auto; /* Habilita el desplazamiento horizontal */
            max-width: 100%;  /* Asegura que no se exceda el tamaño del contenedor */
        }
    </style>
</head>
<body>
    <h1>Visor de Datos</h1>

    <form method="get" action="">
        <label for="tag">Filtrar por Tag:</label>
        <input type="text" name="tag" id="tag" value="<?= htmlspecialchars($tag) ?>">

        <label for="info">Filtrar por Info:</label>
        <input type="text" name="info" id="info" value="<?= htmlspecialchars($info) ?>">

        <button type="submit">Buscar</button>
        <a href="index.php">Limpiar</a>
    </form>

    <p>Total de resultados: <?= $count ?></p>

    <!-- Contenedor con scroll -->
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Order</th>
                    <th>Tag</th>
                    <th>Info</th>
                    <th>Time</th>
                    <th>Client Hash</th>
                    <th>Client Hash Signed</th>
                    <th>New Hash</th>
                    <th>New Hash Signed</th>
                    <th>Last Hash</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($rows as $row): ?>
                <tr>
                    <td><?= htmlspecialchars($row['insertion_order']) ?></td>
                    <td><?= htmlspecialchars($row['tag']) ?></td>
                    <td><?= htmlspecialchars($row['info']) ?></td>
                    <td><?= htmlspecialchars($row['insertion_time']) ?></td>
                    <td><?= htmlspecialchars($row['client_hash']) ?></td>
                    <td><?= htmlspecialchars($row['client_hash_signed']) ?></td>
                    <td><?= htmlspecialchars($row['new_hash']) ?></td>
                    <td><?= htmlspecialchars($row['new_hash_signed']) ?></td>
                    <td><?= htmlspecialchars($row['last_hash']) ?></td>
                </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</body>
</html>

