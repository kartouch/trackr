'use strict';

var app = angular.module('trackr', []);
app.controller('trackr', function ($scope, $http) {

    $http.get("/api/v1/tracks")
        .then(function (response) {
            $scope.tracks = response.data;
            $scope.tracksPaginated = $scope.tracks.slice(0, 30)
            var p = Math.ceil($scope.tracks.length / 30)
            $scope.pages = new Array(p)
        });

    $scope.markAsChecked = track => {
        $http.post("/api/v1/tracks/" + track.id + "/checked")
            .then(
                function (response) {
                    $('#track_' + track.id).hide()
                }
            );
    };


    $scope.paginateTracks = (tracks, page) => {
        if (tracks == undefined) {
            return
        }
        var p = Math.ceil(tracks.length / 30)
        $scope.pages = new Array(p)
        var start = (page * 30) - 30
        var end = start + 29
        var trackList = tracks.slice(start, end)
        $scope.tracksPaginated = trackList
    };

});