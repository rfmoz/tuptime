<html>
<head>
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: #b3b3b3;
        }
        table {
             margin-left: auto;
             margin-right: auto;
             font-size: 105%;
             border-collapse: collapse;
             color: #d7d7d7;
        }
        tr{
             vertical-align:middle;
             background-color: #222222;
	}
        td{
             text-align:center; 
             padding: 15px;
	}
        tr:hover td{
             background-color: #1a1a1a;
	}


        #type-default td {
             border-bottom: 1px solid #111111;
        }
        #type-default td:first-child {
             text-align: left;
             padding-left: 25px;
             color: #00bb55;
             font-weight: bold;
             border-right: 1px solid #111111;
        }


        #type-table td {
             border: 1px solid #111111;
        }
        #type-table tr:first-child td{
             color: #00bb55;
             font-weight: bold;
             border-bottom: 3px solid #111111;
        }


        #type-list td {
             border-bottom: 1px solid #111111;
        }
        #type-list td:first-child {
             text-align: left;
             padding-left: 25px;
             color: #00bb55;
             font-weight: bold;
             border-right: 1px solid #111111;
        }
        #type-list tr:nth-child(4n) td{
             border-bottom: 3px solid #111111;
        }
    </style>

</head>
<body>
    <a href="test.php">Normal</a>
    <a href="test.php?type=table">Table</a>
    <a href="test.php?type=list">List</a>
        <?php

            # Read arguments fron GET method
            if(isset($_GET['type'])) {
                $type = $_GET['type'];
            }

            # Choose the right behaviour
            if (isset($type)) {
                if ($type === 'table') {
                    exec('tuptime -t --csv 2> /dev/null', $output, $return);
                    echo "<table id='type-table'>";
                } else if ($type === 'list') {
                    exec('tuptime -l --csv 2> /dev/null', $output, $return);
                    echo "<table id='type-list'>";
                } else {
                    exec('tuptime --csv 2> /dev/null', $output, $return);
                    echo "<table id='type-default'>";
                }
            } else {
                exec('tuptime --csv 2> /dev/null', $output, $return);
                echo "<table id='type-default'>";
            }

            # Initialize empty array for the table
            $table = [];

            # Create table content based on execution output
            foreach ($output as $row) {

                $column = 0;  // Column counter
                $tmprow = '';  // Temporary row store

                array_push($table, "        <tr>");  // Start creating the row

                $row = str_getcsv($row);  // Parse csv row into the array

                # Create the row content 
                foreach ($row as $cell) {

                    if ($type === 'table') {
                        $tmprow .= "<td>$cell</td>";
                    }

                    else if ($type === 'list') {
                        if (  strpos($tmprow, 'Uptime') !== false 
                            || strpos($tmprow, 'Downtime') !== false 
                            || strpos($tmprow, 'Kernel') !== false ) {
                            switch ($column) {
                                case 1:
                                    $tmprow .= "<td colspan='3'>$cell</td>";
                                    break;
                                default:
                                    $tmprow .= "<td>$cell</td>";
                            }
                        } else {
                            $tmprow .= "<td>$cell</td>";
                        }
                    }

                    else {
                        if (   strpos($tmprow, 'System startups') !== false
                            || strpos($tmprow, 'System uptime') !== false
                            || strpos($tmprow, 'System downtime') !== false
                            || strpos($tmprow, 'Largest uptime') !== false
                            || strpos($tmprow, 'Shortest uptime') !== false 
                            || strpos($tmprow, 'Largest downtime') !== false
                            || strpos($tmprow, 'Shortest downtime') !== false 
                            || strpos($tmprow, 'Current uptime') !== false ) {
                            switch ($column) {
                                case 1:
                                case 3:
                                    $tmprow .= "<td colspan='2'>$cell</td>";
                                    break;
                                default:
                                    $tmprow .= "<td>$cell</td>";
                            }
                        }
                        elseif (   strpos($tmprow, 'System life') !== false
                                || strpos($tmprow, 'Average uptime') !== false 
                                || strpos($tmprow, 'System kernels') !== false 
                                || strpos($tmprow, '...with kernel') !== false 
                                || strpos($tmprow, 'Average downtime') !== false ) {
                            switch ($column) {
                                case 1:
                                    $tmprow .= "<td colspan='5'>$cell</td>";
                                    break;
                                default:
                                    $tmprow .= "<td>$cell</td>";
                            }
                        }
                        else {
                            $tmprow .= "<td>$cell</td>";
                       }
                   }
                   $column++;
                }
                array_push($table, "$tmprow");
                array_push($table, "</tr>\n");
            }

            foreach ($table as $item) {
               echo $item;
            }
        ?>
    </table>
</body>
</html>
