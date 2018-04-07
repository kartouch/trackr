'use strict';

var app = angular.module('trackr', []);
app.controller('trackr', function($scope,$http) {

    $scope.markAsChecked = function(track) {
        // how to check if checkbox is selected or not
        $http.post("/tracks/"+track.id)
        .then(
            function(response){
              // success callback
            }
         );
      };

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('message', {data: 'I\'m connected!'});
    });

    socket.on('tracks', function(tracks) {
        $scope.$apply(function () {
            $scope.tracks = tracks
        });
    });

});