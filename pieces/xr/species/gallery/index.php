<!DOCTYPE html>

<head>

    <link rel="icon" type="image/png" href="favicon.png">
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
    <meta name="author" content="Jakob Kruse" />

    <base target="_blank">

    <title>Critically endangered species gallery</title>

    <style type="text/css">

        @font-face {
            font-family: 'FUCXED CAPS';
            src: local('FUCXED CAPS'); src: local('FUCXED CAPS Regular'); src: local('FUCXEDCAPS-v2'); src: local('FUCXEDCAPSLatin-Regular');
            src: url('FUCXEDCAPSLatin-Regular.otf') format('opentype');
            src: url('FUCXEDCAPSLatin-Regular.woff') format('woff');
            src: url('FUCXEDCAPSLatin-Regular.woff2') format('woff2');
            font-weight: normal;
            font-style: normal;
        }

        body { background-color: #000; font-family: 'FUCXED CAPS'; color: #333; text-transform: uppercase; text-align: center; }
        .figure { display: inline-block; position: relative; margin: 0px; padding: 0px; box-shadow: inset 0 0 0 0px rgba(255,255,255, .2); transition: all .3s 0s; color: #000; }
        .figure:hover { box-shadow: inset 0 0 0 7px rgba(255,255,255, .2); }
        .figure img { display: block; position: relative; z-index: -1; }
        .figure .name { position: absolute; top: 0; left: 0; z-index: -2; }
        .figure a, .figure a:active, .figure a:focus, .figure a:hover, .figure a:visited { border: none; outline: none; -moz-outline-style: none; color: #000; }
        a { color: #555; text-decoration: none; }

    </style>

</head>

<body>

    <?php
        // Get all .png files except the favicon and sort them by upload date
        $images = preg_grep('/favicon\.png$/', glob('*.png'), PREG_GREP_INVERT);
        usort($images, create_function('$a, $b', 'return filemtime($b) - filemtime($a);'));
    ?>

    <h1 style="font-size: 46pt; color: #777; margin-bottom: 3pt;"> <?php echo sizeof($images); ?> critically endangered species </h1>
    <p style="font-size: 20pt; margin-top: 0; margin-bottom: 20pt;">
        <a href="https://www.nature.com/articles/d41586-019-01448-4">1 million species</a> are facing extinction! <br>
        All images below are public domain, <br>
        Click to enlarge and use as you see fit. <br>
        <?php
            if(isset($_GET["svg"])) {
                $zips = glob('endangered_species_svg_*.zip');
                usort($zips, create_function('$a, $b', 'return filemtime($b) - filemtime($a);'));
                echo "<a href=".$zips[0].">ZIP file</a> | <a href='index.php' target='_self'>PNG version</a> | <a href='https://vimeo.com/480221114' target='_blank'>Video</a> | <a href='mailto:wapu@posteo.net'>Contact</a>";
            }
            else {
                $zips = glob('endangered_species_png_*.zip');
                usort($zips, create_function('$a, $b', 'return filemtime($b) - filemtime($a);'));
                echo "<a href=".$zips[0].">ZIP file</a> | <a href='index.php?svg' target='_self'>SVG version</a> | <a href='https://vimeo.com/480221114' target='_blank'>Video</a> | <a href='mailto:wapu@posteo.net'>Contact</a>";
            }
        ?>
    </p>

    <?php
        foreach($images as $png){
            $name = pathinfo($png, PATHINFO_FILENAME);
            if(isset($_GET["svg"]))
                $href = $name.'.svg';
            else
                $href = $name.'.png';
            echo "<div class='figure'><div class='name'>".$name."</div><a href='".$href."' target='new'><img src='thumbs/".$png."' width='300' height='300' alt='".$name."' /></a></div>\n";
        }                 
    ?>

</body>

</html> 