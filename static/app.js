'use strict';

var app = angular.module('trackr', []);
app.controller('trackr', function($scope,$http) {

    $http.get("/api/v1/tracks")
        .then(function(response) {
        $scope.tracks = response.data;
        $scope.tracksPaginated = $scope.tracks.slice(0,10)
        var p = Math.ceil($scope.tracks.length/10)
        $scope.pages = new Array(p)
    }); 

    $scope.markAsChecked = function(track) {
        $http.post("/api/v1/tracks/"+track.id+"/checked")
        .then(
            function(response){
              $('#track_'+track.id).hide()
            }
         );
      };


    $scope.paginateTracks = function(tracks,start){
        if (tracks == undefined){ return }

        var p = Math.ceil(tracks.length/10)
        $scope.pages = new Array(p)
        if (start > 0){ start = start -1 }
        var end = start + 10
        var trackList = tracks.slice(start,end)
        $scope.tracksPaginated = trackList
    };
    
});