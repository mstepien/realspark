from app.database import save_stats, get_aggregate_stats

def test_save_and_get_stats(mock_db_connection):
    # Initial stats should be empty/zero
    initial = get_aggregate_stats()
    assert initial['total_images'] == 0
    
    # Save a record
    stats = {
        "width": 100,
        "height": 200,
        "mean_color": [10.0, 20.0, 30.0],
        "hog_features": [0.1] * 3780
    }
    save_stats("test.jpg", "http://url", stats)
    
    # Check aggregates
    after = get_aggregate_stats()
    assert after['total_images'] == 1
    assert after['avg_width'] == 100
    assert after['avg_height'] == 200
    assert after['avg_color'] == [10.0, 20.0, 30.0]

def test_multiple_images_aggregation(mock_db_connection):
    stats1 = {"width": 100, "height": 100, "mean_color": [0, 0, 0], "hog_features": [0.0]*3780}
    stats2 = {"width": 200, "height": 200, "mean_color": [100, 100, 100], "hog_features": [0.0]*3780}
    
    save_stats("1.jpg", "u1", stats1)
    save_stats("2.jpg", "u2", stats2)
    
    agg = get_aggregate_stats()
    assert agg['total_images'] == 2
    assert agg['avg_width'] == 150
    assert agg['avg_height'] == 150
    assert agg['avg_color'] == [50.0, 50.0, 50.0]
