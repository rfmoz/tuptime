<!DOCTYPE html>
<html lang="en">
<!--
This is a very basic sample Tuptime wrapper made in PHP.
Maybe you can find it usefull as starting point to other particular project.
Compatible with Tuptime 3.4.0 and above.
//-->
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Tuptime Web Wrapper - <?php echo gethostname(); ?></title>
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            background-color: #b3b3b3;
        }
        #links-menu {
            margin: 5px;
            font-size: 110%;
            word-spacing: 20px;
        }
        #links-menu a{
            color: #222222;
            margin: 5px;
            text-decoration: overline;
        }
        #links-menu a:hover{
            background: #222222;
            color: #d7d7d7;
        }
        table {
            margin-left: auto;
            margin-right: auto;
            font-size: 105%;
            border-collapse: collapse;
            color: #d7d7d7;
            table-layout: fixed;
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
        #type-list tr.rowblock{
            border-top: 3px solid #111111;
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
        #error {
            font-size: 125%;
            font-weight: bold;
            text-align: center;
            width: 100%;
        }
        #version {
            margin-top: 2%;
            margin-bottom: 15px;
            color: #808080;
            text-align: center;
            width: 100%;
        }
    </style>
</head>
<body>
    <div id="links-menu">
        <a href="?type=default">&nbsp;Normal&nbsp;</a>
        <a href="?type=table">&nbsp;Table&nbsp;</a>
        <a href="?type=list">&nbsp;List&nbsp;</a>
    </div>
    <?php

        # Read arguments fron GET method
        if(isset($_GET['type'])) {
            $type = $_GET['type'];
        } else {
            $type = 'default';
        }

        # Choose the right behaviour
        if (isset($type)) {
            if ($type === 'table') {
                exec('tuptime -t --csv 2> /dev/null', $output, $return);
                echo "<table id='type-table'>\n";
            } else if ($type === 'list') {
                exec('tuptime -l --csv 2> /dev/null', $output, $return);
                echo "<table id='type-list'>\n";
            } else {
                exec('tuptime --csv 2> /dev/null', $output, $return);
                echo "<table id='type-default'>\n";
            }
        } else {
            exec('tuptime --csv 2> /dev/null', $output, $return);
            echo "<table id='type-default'>\n";
        }

        # Check right execution
        if ($return != 0) {
            echo "<div id='error'>- Error $return -</div>";
            exit(1);
        }

        # Initialize empty array for the table
        $table = [];

        # Create table content based on execution output
        foreach ($output as $row) {

            $column = -1;  // Column counter
            $tmprow = '';  // Temporary row store

            $row = str_getcsv($row);  // Parse csv row into the array

            # Start row adding it into the array
            # For table type
            if ($type === 'table') {
                array_push($table, "        <tr>");
            }
            # For list type
            else if ($type === 'list') {
                if ( in_array('Startup', $row) && count($table) > 1 ) {
                    array_push($table, "        <tr class='rowblock'>");
                }
            }
            # For default type
            else {
                array_push($table, "        <tr>");
            }

            # Create the row content
            foreach ($row as $cell) {

                $column++;  // Increment column counter

                $cell=htmlentities($cell);  // Convert special chars to html

                # For table type
                if ($type === 'table') {
                    $tmprow .= "<td>$cell</td>";
                }

                # For list type
                else if ($type === 'list') {
                    # Match rows with different number of columns and
                    # assign the right colspan to the right column number
                    if (   in_array('Uptime', $row)
                        || in_array('Downtime', $row)
                        || in_array('Kernel', $row) ) {
                        switch ($column) {
                            case 1:
                                $tmprow .= "<td colspan='3'>$cell</td>";
                                continue 2;
                        }
                    }
                    # Default row assignment
                    $tmprow .= "<td>$cell</td>";
                }

                # For default type
                else {
                    # Match rows with different number of columns and
                    # assign the right colspan to the right column number
                    if (   in_array('System uptime', $row)
                        || in_array('System downtime', $row)
                        || in_array('Largest uptime', $row)
                        || in_array('Shortest uptime', $row)
                        || in_array('Largest downtime', $row)
                        || in_array('Shortest downtime', $row)
                        || in_array('Current uptime', $row) ) {
                        switch ($column) {
                            case 1:
                            case 3:
                                $tmprow .= "<td colspan='2'>$cell</td>";
                                continue 2;
                        }
                    }
                    elseif (   in_array('System life', $row)
                            || in_array('Average uptime', $row)
                            || in_array('System kernels', $row)
                            || in_array('...with kernel', $row)
                            || in_array('Average downtime' , $row) ) {
                        switch ($column) {
                            case 1:
                                $tmprow .= "<td colspan='5'>$cell</td>";
                                continue 2;
                        }
                    }
                    elseif (   in_array('System startups', $row) != in_array('until', $row) ) {
                        switch ($column) {
                            case 1:
                            case 3:
                                $tmprow .= "<td colspan='2'>$cell</td>";
                                continue 2;
                            case 4:
                            case 5:
                                continue 2;
                        }
                    }
                    # Default row assignment
                    $tmprow .= "<td>$cell</td>";
               }
            }
            array_push($table, "$tmprow");  // Add row into table array
            array_push($table, "</tr>\n");  // Add end of table row into array
        }

        # Print table content
        foreach ($table as $item) {
           echo $item;
        }
    ?>
    </table>
    <div id="version">
        <?php
            exec('tuptime -V 2> /dev/null', $v_output);
            echo current($v_output) . "\n";
        ?>
    </div>
</body>
</html>
